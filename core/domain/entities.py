from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Choice:
    id: Optional[int]
    text: str
    votes: int = 0

@dataclass
class Question:
    id: Optional[int]
    text: str
    pub_date: datetime
    choices: List[Choice] = field(default_factory=list)

    # Blockchain specific
    blockchain_id: Optional[int] = None
    is_synced: bool = False
    tx_hash: Optional[str] = None

@dataclass
class Vote:
    question_id: int
    choice_index: int
    voter_address: str
    transaction_hash: str
    block_number: int
    log_index: int
    timestamp: Optional[datetime] = None
