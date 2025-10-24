"""
Web3 Services for VotingContract Integration
"""

from .config import get_web3, get_contract, is_web3_connected, web3_manager
from web3.exceptions import ContractLogicError, Web3Exception
from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BlockchainVotingService:
    """
    Service class for interacting with the VotingContract smart contract
    """
    
    def __init__(self):
        self.web3 = get_web3()
        self.contract = get_contract()
        self.default_account = web3_manager.get_default_account()
    
    def is_available(self) -> bool:
        """Check if blockchain service is available"""
        return is_web3_connected() and self.contract is not None
    
    def get_contract_info(self) -> Dict[str, Any]:
        """Get basic contract information"""
        if not self.is_available():
            return {"error": "Blockchain not available"}
        
        try:
            question_counter = self.contract.functions.questionCounter().call()
            owner = self.contract.functions.owner().call()
            
            return {
                "contract_address": self.contract.address,
                "question_counter": question_counter,
                "owner": owner,
                "is_connected": True
            }
        except Exception as e:
            logger.error(f"Error getting contract info: {e}")
            return {"error": str(e), "is_connected": False}
    
    def create_question_on_blockchain(self, question_text: str, choices: List[str]) -> Dict[str, Any]:
        """
        Create a question on the blockchain
        
        Args:
            question_text (str): The question text
            choices (List[str]): List of choice options
            
        Returns:
            Dict[str, Any]: Transaction result and question ID
        """
        if not self.is_available():
            return {"success": False, "error": "Blockchain not available"}
        
        if len(choices) < 2:
            return {"success": False, "error": "Minimum 2 choices required"}
        
        if len(choices) > 10:
            return {"success": False, "error": "Maximum 10 choices allowed"}
        
        try:
            # Build transaction
            transaction = self.contract.functions.createQuestion(
                question_text, 
                choices
            ).build_transaction({
                'from': self.default_account,
                'gas': 2000000,  # Sufficient gas limit
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(self.default_account),
            })
            
            # Sign and send transaction
            # Note: In production, you'd use a proper private key management
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Hardhat account #0 private key
            )
            
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Extract question ID from events
            question_created_events = self.contract.events.QuestionCreated().process_receipt(receipt)
            question_id = None
            if question_created_events:
                question_id = question_created_events[0]['args']['questionId']
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "question_id": question_id,
                "gas_used": receipt['gasUsed']
            }
            
        except ContractLogicError as e:
            logger.error(f"Contract logic error: {e}")
            return {"success": False, "error": f"Contract error: {e}"}
        except Exception as e:
            logger.error(f"Error creating question on blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def get_question_from_blockchain(self, question_id: int) -> Dict[str, Any]:
        """
        Get question details from blockchain
        
        Args:
            question_id (int): The question ID
            
        Returns:
            Dict[str, Any]: Question details
        """
        if not self.is_available():
            return {"success": False, "error": "Blockchain not available"}
        
        try:
            result = self.contract.functions.getQuestion(question_id).call()
            
            return {
                "success": True,
                "question_text": result[0],
                "choices": result[1],
                "is_active": result[2],
                "total_votes": result[3]
            }
            
        except Exception as e:
            logger.error(f"Error getting question from blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def vote_on_blockchain(self, question_id: int, choice_index: int, voter_address: str = None) -> Dict[str, Any]:
        """
        Cast a vote on the blockchain
        
        Args:
            question_id (int): The question ID
            choice_index (int): Index of the chosen option
            voter_address (str, optional): Voter's address. Defaults to default account.
            
        Returns:
            Dict[str, Any]: Voting result
        """
        if not self.is_available():
            return {"success": False, "error": "Blockchain not available"}
        
        voter = voter_address or self.default_account
        
        try:
            # Check if user has already voted
            has_voted = self.contract.functions.hasUserVoted(voter, question_id).call()
            if has_voted:
                return {"success": False, "error": "User has already voted on this question"}
            
            # Build transaction
            transaction = self.contract.functions.vote(
                question_id, 
                choice_index
            ).build_transaction({
                'from': voter,
                'gas': 200000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(voter),
            })
            
            # Sign and send transaction
            signed_txn = self.web3.eth.account.sign_transaction(
                transaction, 
                private_key="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Hardhat account #0
            )
            
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "transaction_hash": tx_hash.hex(),
                "gas_used": receipt['gasUsed']
            }
            
        except ContractLogicError as e:
            logger.error(f"Contract logic error during voting: {e}")
            return {"success": False, "error": f"Voting error: {e}"}
        except Exception as e:
            logger.error(f"Error voting on blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def get_vote_results_from_blockchain(self, question_id: int) -> Dict[str, Any]:
        """
        Get voting results for a question from blockchain
        
        Args:
            question_id (int): The question ID
            
        Returns:
            Dict[str, Any]: Voting results with vote counts per choice
        """
        if not self.is_available():
            return {"success": False, "error": "Blockchain not available"}
        
        try:
            # Get question details first
            question_data = self.get_question_from_blockchain(question_id)
            if not question_data["success"]:
                return question_data
            
            choices = question_data["choices"]
            total_votes = question_data["total_votes"]
            
            # Get votes for each choice
            vote_results = []
            for i, choice in enumerate(choices):
                votes = self.contract.functions.getVotes(question_id, i).call()
                percentage = (votes * 100 / total_votes) if total_votes > 0 else 0
                
                vote_results.append({
                    "choice": choice,
                    "votes": votes,
                    "percentage": round(percentage, 1)
                })
            
            return {
                "success": True,
                "question_text": question_data["question_text"],
                "total_votes": total_votes,
                "results": vote_results,
                "is_active": question_data["is_active"]
            }
            
        except Exception as e:
            logger.error(f"Error getting vote results from blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def get_all_questions_from_blockchain(self) -> Dict[str, Any]:
        """
        Get all questions from blockchain
        
        Returns:
            Dict[str, Any]: List of all questions
        """
        if not self.is_available():
            return {"success": False, "error": "Blockchain not available"}
        
        try:
            question_counter = self.contract.functions.questionCounter().call()
            questions = []
            
            for i in range(question_counter):
                question_data = self.get_question_from_blockchain(i)
                if question_data["success"]:
                    questions.append({
                        "id": i,
                        **question_data
                    })
            
            return {
                "success": True,
                "questions": questions,
                "total_count": question_counter
            }
            
        except Exception as e:
            logger.error(f"Error getting all questions from blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def check_user_voted(self, user_address: str, question_id: int) -> bool:
        """
        Check if a user has voted on a specific question
        
        Args:
            user_address (str): User's wallet address
            question_id (int): Question ID
            
        Returns:
            bool: True if user has voted, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            return self.contract.functions.hasUserVoted(user_address, question_id).call()
        except Exception as e:
            logger.error(f"Error checking if user voted: {e}")
            return False


# Global service instance
blockchain_service = BlockchainVotingService()