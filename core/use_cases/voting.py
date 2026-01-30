from typing import Dict, Any, List
from core.domain.interfaces import IVoteRepository, IQuestionRepository
from core.domain.entities import Question

class GetQuestionResultsUseCase:
    def __init__(self, question_repo: IQuestionRepository, vote_repo: IVoteRepository):
        self.question_repo = question_repo
        self.vote_repo = vote_repo

    def execute(self, question_id: int) -> Dict[str, Any]:
        question = self.question_repo.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")

        votes = self.vote_repo.get_votes_for_question(question_id)

        # Aggregate results
        # Initialize counts
        results = {choice.id: 0 for choice in question.choices} if question.choices else {}
        # We might need to handle choice by index if ID is not available or consistent

        # If choices are just strings in the entity or handled by index in blockchain
        # The blockchain uses index.

        # Let's map choice index to choice text/object
        choice_map = {i: c for i, c in enumerate(question.choices)}
        vote_counts = {i: 0 for i in range(len(question.choices))}

        total_votes = 0
        for vote in votes:
            if vote.choice_index in vote_counts:
                vote_counts[vote.choice_index] += 1
                total_votes += 1

        # Format output
        formatted_choices = []
        for i, choice in enumerate(question.choices):
            count = vote_counts.get(i, 0)
            percentage = (count / total_votes * 100) if total_votes > 0 else 0
            formatted_choices.append({
                'text': choice.text,
                'votes': count,
                'percentage': round(percentage, 1)
            })

        return {
            'question_text': question.text,
            'total_votes': total_votes,
            'choices': formatted_choices,
            'is_synced': question.is_synced
        }
