from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from .entities import Question, Vote

class IQuestionRepository(ABC):
    @abstractmethod
    def get_by_id(self, question_id: int) -> Optional[Question]:
        pass

    @abstractmethod
    def get_by_blockchain_id(self, blockchain_id: int) -> Optional[Question]:
        pass

    @abstractmethod
    def save(self, question: Question) -> Question:
        pass

    @abstractmethod
    def get_pending_sync(self) -> List[Question]:
        pass

class IVoteRepository(ABC):
    @abstractmethod
    def save(self, vote: Vote) -> Vote:
        pass

    @abstractmethod
    def exists(self, transaction_hash: str, log_index: int) -> bool:
        pass

    @abstractmethod
    def get_votes_for_question(self, question_id: int) -> List[Vote]:
        pass

class IBlockchainGateway(ABC):
    @abstractmethod
    def fetch_vote_events(self, from_block: int) -> List[Dict[str, Any]]:
        """
        Returns a list of event data dicts.
        Each dict should contain: question_id, choice_index, voter, tx_hash, block_number, log_index
        """
        pass

    @abstractmethod
    def create_question(self, text: str, choices: List[str]) -> Dict[str, Any]:
        """
        Returns dict with success, transaction_hash, question_id (if available immediately)
        """
        pass

    @abstractmethod
    def get_current_block_number(self) -> int:
        pass
