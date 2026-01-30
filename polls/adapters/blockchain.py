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


class MockBlockchainGateway(IBlockchainGateway):
    """Gateway simulado para testing sin blockchain real
    
    Este gateway permite ejecutar tests y desarrollo sin necesidad de
    tener un nodo blockchain corriendo. Simula transacciones y eventos.
    """
    
    def __init__(self):
        self._mock_events: List[Dict[str, Any]] = []
        self._mock_questions: Dict[int, Dict[str, Any]] = {}
        self._current_block = 0
        logger.info("MockBlockchainGateway initialized")
    
    def fetch_vote_events(self, from_block: int) -> List[Dict[str, Any]]:
        """Retorna eventos simulados desde el bloque especificado"""
        filtered_events = [
            e for e in self._mock_events 
            if e['block_number'] >= from_block
        ]
        logger.info(f"[MOCK] Fetched {len(filtered_events)} vote events from block {from_block}")
        return filtered_events
    
    def create_question(self, text: str, choices: List[str]) -> Dict[str, Any]:
        """Simula creación de pregunta en blockchain"""
        import hashlib
        import time
        
        mock_id = len(self._mock_questions)
        mock_tx = "0x" + hashlib.sha256(
            f"{text}{time.time()}".encode()
        ).hexdigest()
        
        self._mock_questions[mock_id] = {
            'text': text,
            'choices': choices,
            'created_at': time.time()
        }
        
        logger.info(f"[MOCK] Created question {mock_id}: {text}")
        
        return {
            "success": True,
            "question_id": mock_id,
            "transaction_hash": mock_tx
        }
    
    def get_current_block_number(self) -> int:
        """Retorna número de bloque simulado"""
        return self._current_block
    
    # Métodos helper para testing
    def add_mock_vote_event(self, question_id: int, choice_index: int, 
                           voter: str, tx_hash: str = None):
        """Agrega evento de voto simulado para testing
        
        Args:
            question_id: ID de la pregunta en blockchain
            choice_index: Índice de la opción votada
            voter: Dirección de la wallet del votante
            tx_hash: Hash de transacción (opcional, se genera si no se provee)
        """
        if tx_hash is None:
            import hashlib, time
            tx_hash = "0x" + hashlib.sha256(
                f"{question_id}{choice_index}{voter}{time.time()}".encode()
            ).hexdigest()
        
        self._current_block += 1
        
        event = {
            'question_id': question_id,
            'choice_index': choice_index,
            'voter': voter,
            'tx_hash': tx_hash,
            'block_number': self._current_block,
            'log_index': len(self._mock_events)
        }
        
        self._mock_events.append(event)
        logger.info(f"[MOCK] Added vote event for question {question_id} by {voter}")
    
    def reset(self):
        """Resetea estado del mock - útil para tests"""
        self._mock_events.clear()
        self._mock_questions.clear()
        self._current_block = 0
        logger.info("[MOCK] Gateway reset")
