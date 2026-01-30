"""
Hybrid Django-Blockchain Models

These models extend the existing Django models with blockchain functionality,
allowing questions and votes to be stored both in Django database and on blockchain.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from polls.models import Question as BaseQuestion, Choice as BaseChoice
from .services import blockchain_service
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BlockchainQuestion(BaseQuestion):
    """
    Extended Question model with blockchain integration
    """
    # Blockchain-specific fields
    blockchain_id = models.IntegerField(null=True, blank=True, help_text="Question ID on blockchain")
    blockchain_tx_hash = models.CharField(max_length=66, null=True, blank=True, help_text="Transaction hash of creation")
    is_blockchain_synced = models.BooleanField(default=False, help_text="Is synced with blockchain")
    use_blockchain = models.BooleanField(default=False, help_text="Use blockchain for this question")
    blockchain_created_at = models.DateTimeField(null=True, blank=True, help_text="When created on blockchain")
    
    # Custom manager (will be defined later)
    objects = None  # Will be set after manager class definition
    
    class Meta:
        verbose_name = "Blockchain Question"
        verbose_name_plural = "Blockchain Questions"
        ordering = ['-pub_date']
    
    def __str__(self):
        blockchain_status = "🔗" if self.is_blockchain_synced else "💾"
        return f"{blockchain_status} {self.question_text}"
    
    def save(self, *args, **kwargs):
        """Override save to handle blockchain creation"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # If new question and blockchain is enabled, create on blockchain
        if is_new and self.use_blockchain and blockchain_service.is_available():
            self.create_on_blockchain()
    
    def create_on_blockchain(self) -> Dict[str, Any]:
        """
        Create this question on the blockchain
        
        Returns:
            Dict[str, Any]: Result of blockchain creation
        """
        if not self.use_blockchain:
            return {"success": False, "error": "Blockchain not enabled for this question"}
        
        if self.is_blockchain_synced:
            return {"success": False, "error": "Question already exists on blockchain"}
        
        # Get choices as list of strings
        choices = list(self.choice_set.values_list('choice_text', flat=True))
        
        if len(choices) < 2:
            return {"success": False, "error": "Minimum 2 choices required for blockchain"}
        
        try:
            # If blockchain service is not available, use enhanced mock mode
            if not blockchain_service.is_available():
                # Mock mode: simulate successful blockchain creation
                import hashlib
                import time
                
                mock_id = hash(f"{self.question_text}{time.time()}") % 10000
                mock_tx_hash = "0x" + hashlib.sha256(
                    f"{self.question_text}{mock_id}".encode()
                ).hexdigest()[:64]
                
                result = {
                    "success": True,
                    "question_id": mock_id,
                    "transaction_hash": mock_tx_hash,
                    "mock": True
                }
                
                logger.info(f"Mock blockchain creation for '{self.question_text}'")
            else:
                result = blockchain_service.create_question_on_blockchain(
                    self.question_text, 
                    choices
                )
            
            if result.get("success"):
                # Update blockchain fields
                self.blockchain_id = result.get("question_id")
                self.blockchain_tx_hash = result.get("transaction_hash")
                self.is_blockchain_synced = True
                self.blockchain_created_at = timezone.now()
                
                # Save without triggering create_on_blockchain again
                super().save(update_fields=[
                    'blockchain_id', 'blockchain_tx_hash', 
                    'is_blockchain_synced', 'blockchain_created_at'
                ])
                
                status = "(mock)" if result.get("mock") else "(real)"
                logger.info(f"Question '{self.question_text}' created on blockchain {status} with ID {self.blockchain_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating question on blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def sync_from_blockchain(self) -> Dict[str, Any]:
        """
        Sync question data from blockchain
        
        Returns:
            Dict[str, Any]: Blockchain question data
        """
        if not self.is_blockchain_synced or self.blockchain_id is None:
            return {"success": False, "error": "Question not on blockchain"}
        
        try:
            result = blockchain_service.get_question_from_blockchain(self.blockchain_id)
            
            if result.get("success"):
                # Update local data if different
                blockchain_text = result.get("question_text")
                if blockchain_text != self.question_text:
                    logger.warning(f"Question text mismatch: DB='{self.question_text}' vs Blockchain='{blockchain_text}'")
            
            return result
            
        except Exception as e:
            logger.error(f"Error syncing from blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def get_blockchain_results(self) -> Dict[str, Any]:
        """
        Get voting results from blockchain
        
        Returns:
            Dict[str, Any]: Voting results
        """
        if not self.is_blockchain_synced or self.blockchain_id is None:
            return {"success": False, "error": "Question not on blockchain"}
        
        try:
            return blockchain_service.get_vote_results_from_blockchain(self.blockchain_id)
        except Exception as e:
            logger.error(f"Error getting blockchain results: {e}")
            return {"success": False, "error": str(e)}
    
    def vote_on_blockchain(self, choice_index: int, voter_address: str = None) -> Dict[str, Any]:
        """
        Cast a vote on blockchain
        
        Args:
            choice_index (int): Index of choice to vote for
            voter_address (str, optional): Voter's address
            
        Returns:
            Dict[str, Any]: Voting result
        """
        if not self.is_blockchain_synced or self.blockchain_id is None:
            return {"success": False, "error": "Question not on blockchain"}
        
        try:
            return blockchain_service.vote_on_blockchain(
                self.blockchain_id, 
                choice_index, 
                voter_address
            )
        except Exception as e:
            logger.error(f"Error voting on blockchain: {e}")
            return {"success": False, "error": str(e)}
    
    def is_blockchain_available(self) -> bool:
        """Check if blockchain functionality is available"""
        return self.use_blockchain and blockchain_service.is_available()
    
    def get_hybrid_results(self) -> Dict[str, Any]:
        """
        Get results from both Django database and blockchain
        
        Returns:
            Dict[str, Any]: Combined results
        """
        results = {
            "question_text": self.question_text,
            "django_results": [],
            "blockchain_results": None,
            "is_blockchain_synced": self.is_blockchain_synced
        }
        
        # Get Django results
        for choice in self.choice_set.all():
            results["django_results"].append({
                "choice": choice.choice_text,
                "votes": choice.votes
            })
        
        # Get blockchain results if available
        if self.is_blockchain_synced:
            blockchain_data = self.get_blockchain_results()
            if blockchain_data.get("success"):
                results["blockchain_results"] = blockchain_data.get("results", [])
        
        return results


class BlockchainChoice(BaseChoice):
    """
    Extended Choice model with blockchain awareness
    """
    # This model mainly serves as a bridge to track Django choices
    # The actual blockchain voting is handled at the Question level
    
    class Meta:
        verbose_name = "Blockchain Choice"
        verbose_name_plural = "Blockchain Choices"
    
    def vote_on_blockchain(self, voter_address: str = None) -> Dict[str, Any]:
        """
        Vote for this choice on blockchain
        
        Args:
            voter_address (str, optional): Voter's address
            
        Returns:
            Dict[str, Any]: Voting result
        """
        if not hasattr(self.question, 'blockchainquestion'):
            return {"success": False, "error": "Question not blockchain-enabled"}
        
        blockchain_question = self.question.blockchainquestion
        
        # Find choice index
        choice_index = None
        choices = list(blockchain_question.choice_set.all())
        
        for i, choice in enumerate(choices):
            if choice.id == self.id:
                choice_index = i
                break
        
        if choice_index is None:
            return {"success": False, "error": "Choice not found"}
        
        return blockchain_question.vote_on_blockchain(choice_index, voter_address)


class BlockchainVote(models.Model):
    """
    Track blockchain votes locally for reference
    """
    question = models.ForeignKey(BlockchainQuestion, on_delete=models.CASCADE)
    choice_index = models.IntegerField()
    voter_address = models.CharField(max_length=42, help_text="Ethereum wallet address")
    transaction_hash = models.CharField(max_length=66)
    block_number = models.IntegerField(null=True, blank=True)
    log_index = models.IntegerField(default=0, help_text="Event log index for idempotency")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Blockchain Vote"
        verbose_name_plural = "Blockchain Votes"
        unique_together = ['question', 'voter_address']  # One vote per address per question
        indexes = [
            models.Index(fields=['transaction_hash', 'log_index'], name='tx_log_index_idx'),
        ]
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Vote by {self.voter_address[:10]}... on Q{self.question.id}"
    
    @property
    def choice_text(self):
        """Get the choice text for this vote"""
        try:
            choices = list(self.question.choice_set.all())
            if 0 <= self.choice_index < len(choices):
                return choices[self.choice_index].choice_text
            return "Unknown choice"
        except:
            return "Error getting choice"


# Manager for easier access
class BlockchainQuestionManager(models.Manager):
    """Manager for BlockchainQuestion with useful methods"""
    
    def blockchain_enabled(self):
        """Get questions with blockchain enabled"""
        return self.filter(use_blockchain=True)
    
    def synced_with_blockchain(self):
        """Get questions synced with blockchain"""
        return self.filter(is_blockchain_synced=True)
    
    def pending_blockchain_sync(self):
        """Get questions that should be on blockchain but aren't synced"""
        return self.filter(use_blockchain=True, is_blockchain_synced=False)
    
    def create_with_blockchain(self, question_text: str, choices: List[str], 
                              pub_date=None, use_blockchain=True):
        """
        Create a question with choices and optionally put it on blockchain
        
        Args:
            question_text (str): The question text
            choices (List[str]): List of choice texts
            pub_date: Publication date (defaults to now)
            use_blockchain (bool): Whether to use blockchain
            
        Returns:
            BlockchainQuestion: The created question
        """
        if pub_date is None:
            pub_date = timezone.now()
        
        # Create question
        question = self.create(
            question_text=question_text,
            pub_date=pub_date,
            use_blockchain=use_blockchain
        )
        
        # Create choices
        for choice_text in choices:
            BlockchainChoice.objects.create(
                question=question,
                choice_text=choice_text
            )
        
        # Create on blockchain if enabled
        if use_blockchain and blockchain_service.is_available():
            result = question.create_on_blockchain()
            logger.info(f"Blockchain creation result: {result}")
        
        return question


# Add custom manager to BlockchainQuestion
BlockchainQuestion.objects = BlockchainQuestionManager()
BlockchainQuestion.objects.model = BlockchainQuestion
