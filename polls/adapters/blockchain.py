from typing import List, Dict, Any
import logging
from django.conf import settings
from core.domain.interfaces import IBlockchainGateway
from polls.blockchain.config import get_web3, get_contract, is_web3_connected, web3_manager

logger = logging.getLogger(__name__)

class Web3BlockchainGateway(IBlockchainGateway):
    def __init__(self):
        pass

    @property
    def web3(self):
        return get_web3()

    @property
    def contract(self):
        return get_contract()

    def _is_available(self):
        return is_web3_connected() and self.contract is not None

    def fetch_vote_events(self, from_block: int) -> List[Dict[str, Any]]:
        if not self._is_available():
            logger.warning("Blockchain not available for fetching events")
            return []

        try:
            # Fetch logs
            # We use get_logs from the contract event
            events = self.contract.events.VoteCast().get_logs(fromBlock=from_block)

            results = []
            for event in events:
                results.append({
                    'question_id': event['args']['questionId'],
                    'choice_index': event['args']['choiceIndex'],
                    'voter': event['args']['voter'],
                    'tx_hash': event['transactionHash'].hex(),
                    'block_number': event['blockNumber'],
                    'log_index': event['logIndex']
                })

            logger.info(f"Fetched {len(results)} vote events from block {from_block}")
            return results

        except Exception as e:
            logger.error(f"Error fetching vote events: {e}")
            return []

    def create_question(self, text: str, choices: List[str]) -> Dict[str, Any]:
        if not self._is_available():
            # Mock behavior if needed, or failure
            # For this gateway, we might want to return failure and let the caller handle mock logic
            # OR implement mock logic here if this adapter is supposed to handle the "mock mode".
            # Given the existing code had mock logic in models.py (which is bad),
            # ideally we move it here or to a MockBlockchainGateway.
            # For now, let's return error and let the Controller/UseCase decide,
            # OR we implement the mock here.

            # Let's try to implement a basic mock response if strictly needed,
            # but usually Gateway should just interface with external system.
            return {"success": False, "error": "Blockchain not available"}

        try:
            default_account = web3_manager.get_default_account()

            # Build transaction
            transaction = self.contract.functions.createQuestion(
                text,
                choices
            ).build_transaction({
                'from': default_account,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(default_account),
            })

            # Sign and send (using Hardhat account #0 private key for dev)
            private_key = getattr(settings, 'BLOCKCHAIN_PRIVATE_KEY', "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction,
                private_key=private_key
            )

            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            # Extract ID
            question_created_events = self.contract.events.QuestionCreated().process_receipt(receipt)
            question_id = None
            if question_created_events:
                question_id = question_created_events[0]['args']['questionId']

            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "question_id": question_id
            }
        except Exception as e:
            logger.error(f"Error creating question on blockchain: {e}")
            return {"success": False, "error": str(e)}

    def get_current_block_number(self) -> int:
        if not self._is_available():
            return 0
        try:
            return self.web3.eth.block_number
        except Exception:
            return 0
