from typing import List, Dict, Any
import logging
from core.domain.interfaces import IVoteRepository, IQuestionRepository, IBlockchainGateway
from core.domain.entities import Vote

logger = logging.getLogger(__name__)

class SyncVotesUseCase:
    def __init__(self,
                 vote_repo: IVoteRepository,
                 question_repo: IQuestionRepository,
                 blockchain_gateway: IBlockchainGateway):
        self.vote_repo = vote_repo
        self.question_repo = question_repo
        self.blockchain_gateway = blockchain_gateway

    def execute(self, from_block: int = 0) -> int:
        """
        Syncs votes from blockchain starting from from_block.
        Returns the number of new votes synced.
        """
        logger.info(f"Starting vote sync from block {from_block}")

        events = self.blockchain_gateway.fetch_vote_events(from_block)
        new_votes_count = 0

        for event in events:
            # Event data expected:
            # question_id (blockchain), choice_index, voter, tx_hash, block_number, log_index

            tx_hash = event['tx_hash']
            log_index = event['log_index']

            # Idempotency check
            if self.vote_repo.exists(tx_hash, log_index):
                logger.debug(f"Vote {tx_hash}-{log_index} already exists. Skipping.")
                continue

            blockchain_question_id = event['question_id']
            question = self.question_repo.get_by_blockchain_id(blockchain_question_id)

            if not question:
                logger.warning(f"Question with blockchain ID {blockchain_question_id} not found locally. Skipping vote.")
                continue

            vote = Vote(
                question_id=question.id,
                choice_index=event['choice_index'],
                voter_address=event['voter'],
                transaction_hash=tx_hash,
                block_number=event['block_number'],
                log_index=log_index
            )

            self.vote_repo.save(vote)
            new_votes_count += 1
            logger.info(f"Synced new vote for Question {question.id} from {event['voter']}")

        return new_votes_count
