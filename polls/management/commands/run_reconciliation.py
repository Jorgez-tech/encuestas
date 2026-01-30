from django.core.management.base import BaseCommand
from polls.adapters.repositories import DjangoVoteRepository, DjangoQuestionRepository
from polls.adapters.blockchain import Web3BlockchainGateway
from core.use_cases.sync import SyncVotesUseCase

class Command(BaseCommand):
    help = 'Reconciles votes from blockchain to local database'

    def add_arguments(self, parser):
        parser.add_argument('--from-block', type=int, default=0, help='Block number to start syncing from')

    def handle(self, *args, **options):
        vote_repo = DjangoVoteRepository()
        question_repo = DjangoQuestionRepository()
        gateway = Web3BlockchainGateway()

        use_case = SyncVotesUseCase(vote_repo, question_repo, gateway)

        from_block = options['from_block']

        self.stdout.write(f"Starting sync from block {from_block}...")
        try:
            count = use_case.execute(from_block=from_block)
            self.stdout.write(self.style.SUCCESS(f'Successfully synced {count} votes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error syncing votes: {e}'))
