from typing import List, Optional
from django.db import transaction
from core.domain.interfaces import IQuestionRepository, IVoteRepository
from core.domain.entities import Question as QuestionEntity, Vote as VoteEntity, Choice as ChoiceEntity
from polls.blockchain.models import BlockchainQuestion, BlockchainVote, BlockchainChoice
from polls.models import Question as DjangoQuestion

class DjangoQuestionRepository(IQuestionRepository):
    def get_by_id(self, question_id: int) -> Optional[QuestionEntity]:
        try:
            # Try to get as BlockchainQuestion first
            q = BlockchainQuestion.objects.get(pk=question_id)
            return self._to_entity(q)
        except BlockchainQuestion.DoesNotExist:
            try:
                # Fallback to standard Question
                q = DjangoQuestion.objects.get(pk=question_id)
                # Check if it's actually a BlockchainQuestion instance but we caught exception because of how get works?
                # No, standard get on Child model raises DoesNotExist if record is only in Parent table (unlikely)
                # or if record doesn't exist.
                # If we are here, it might be a plain Question.
                # We can return a QuestionEntity with no blockchain info.
                return self._to_entity(q)
            except DjangoQuestion.DoesNotExist:
                return None

    def get_by_blockchain_id(self, blockchain_id: int) -> Optional[QuestionEntity]:
        try:
            q = BlockchainQuestion.objects.get(blockchain_id=blockchain_id)
            return self._to_entity(q)
        except BlockchainQuestion.DoesNotExist:
            return None

    @transaction.atomic
    def save(self, question: QuestionEntity) -> QuestionEntity:
        defaults = {
            'question_text': question.text,
            'pub_date': question.pub_date,
            'blockchain_tx_hash': question.tx_hash,
            'is_blockchain_synced': question.is_synced,
            'use_blockchain': True if question.blockchain_id is not None else False
        }

        bq = None

        # If we have an internal ID, update by it
        if question.id:
            bq, _ = BlockchainQuestion.objects.update_or_create(
                pk=question.id,
                defaults=defaults
            )
            # update_or_create might not update blockchain_id if it's not in defaults
            # (it is not in defaults above to avoid overwriting with None if logic was different)
            if question.blockchain_id is not None:
                bq.blockchain_id = question.blockchain_id
                bq.save()

        # If we have blockchain ID but no internal ID, try to find by blockchain ID
        elif question.blockchain_id is not None:
            bq, _ = BlockchainQuestion.objects.update_or_create(
                blockchain_id=question.blockchain_id,
                defaults=defaults
            )

        # Otherwise create new
        else:
            bq = BlockchainQuestion.objects.create(**defaults)
            if question.blockchain_id is not None:
                bq.blockchain_id = question.blockchain_id
                bq.save()

        if bq:
            question.id = bq.id

        return question

    def get_pending_sync(self) -> List[QuestionEntity]:
        qs = BlockchainQuestion.objects.pending_blockchain_sync()
        return [self._to_entity(q) for q in qs]

    def _to_entity(self, model) -> QuestionEntity:
        # Handle both BlockchainQuestion and regular Question
        is_blockchain = isinstance(model, BlockchainQuestion) or hasattr(model, 'blockchainquestion')

        if hasattr(model, 'blockchainquestion'):
            model = model.blockchainquestion
            is_blockchain = True

        choices = [
            ChoiceEntity(id=c.id, text=c.choice_text, votes=c.votes)
            for c in model.choice_set.all()
        ]

        blockchain_id = model.blockchain_id if is_blockchain else None
        is_synced = model.is_blockchain_synced if is_blockchain else False
        tx_hash = model.blockchain_tx_hash if is_blockchain else None

        return QuestionEntity(
            id=model.id,
            text=model.question_text,
            pub_date=model.pub_date,
            choices=choices,
            blockchain_id=blockchain_id,
            is_synced=is_synced,
            tx_hash=tx_hash
        )

class DjangoVoteRepository(IVoteRepository):
    @transaction.atomic
    def save(self, vote: VoteEntity) -> VoteEntity:
        # Find related question
        try:
            question = BlockchainQuestion.objects.get(pk=vote.question_id)
        except BlockchainQuestion.DoesNotExist:
            # Maybe the entity ID refers to blockchain ID?
            # No, the UseCase resolves local question before calling save.
            # But wait, SyncVotesUseCase calls question_repo.get_by_blockchain_id
            # which returns an Entity with local ID.
            # So vote.question_id is the local ID.
            raise ValueError(f"Question {vote.question_id} not found")

        BlockchainVote.objects.create(
            question=question,
            choice_index=vote.choice_index,
            voter_address=vote.voter_address,
            transaction_hash=vote.transaction_hash,
            block_number=vote.block_number,
            log_index=vote.log_index
        )
        return vote

    def exists(self, transaction_hash: str, log_index: int) -> bool:
        return BlockchainVote.objects.filter(
            transaction_hash=transaction_hash,
            log_index=log_index
        ).exists()

    def get_votes_for_question(self, question_id: int) -> List[VoteEntity]:
        votes = BlockchainVote.objects.filter(question_id=question_id)
        return [
            VoteEntity(
                question_id=v.question.id,
                choice_index=v.choice_index,
                voter_address=v.voter_address,
                transaction_hash=v.transaction_hash,
                block_number=v.block_number or 0,
                log_index=v.log_index,
                timestamp=v.timestamp
            )
            for v in votes
        ]
