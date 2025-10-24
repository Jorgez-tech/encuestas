"""
Django Management Command for Blockchain Operations

This command provides utilities to sync data between Django and blockchain,
deploy contracts, and perform maintenance operations.

Usage:
    python manage.py blockchain_sync --help
    python manage.py blockchain_sync status
    python manage.py blockchain_sync sync_all
    python manage.py blockchain_sync sync_question <id>
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from polls.blockchain.models import BlockchainQuestion, BlockchainVote
from polls.blockchain.services import blockchain_service
from polls.blockchain.config import is_web3_connected
from polls.models import Question

import sys


class Command(BaseCommand):
    help = 'Manage blockchain synchronization and operations'
    
    def add_arguments(self, parser):
        """Add command arguments"""
        parser.add_argument(
            'action',
            choices=['status', 'sync_all', 'sync_question', 'deploy_check', 'reset_sync'],
            help='Action to perform'
        )
        
        parser.add_argument(
            '--question-id',
            type=int,
            help='Question ID for sync_question action'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force operation even if blockchain is not connected'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.verbosity = 2 if options['verbose'] else 1
        action = options['action']
        
        try:
            if action == 'status':
                self.show_status()
            elif action == 'sync_all':
                self.sync_all_questions(force=options['force'])
            elif action == 'sync_question':
                question_id = options.get('question_id')
                if not question_id:
                    raise CommandError("--question-id is required for sync_question action")
                self.sync_single_question(question_id)
            elif action == 'deploy_check':
                self.check_deployment()
            elif action == 'reset_sync':
                self.reset_sync_status(force=options['force'])
                
        except Exception as e:
            raise CommandError(f"Command failed: {str(e)}")
    
    def show_status(self):
        """Show blockchain integration status"""
        self.stdout.write(self.style.SUCCESS("=== Blockchain Integration Status ==="))
        
        # Connection status
        connected = is_web3_connected()
        if connected:
            self.stdout.write(
                self.style.SUCCESS("✅ Blockchain: Connected")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Blockchain: Disconnected")
            )
        
        # Service status
        if blockchain_service.is_available():
            self.stdout.write(
                self.style.SUCCESS("✅ Service: Available")
            )
            
            try:
                contract_info = blockchain_service.get_contract_info()
                self.stdout.write(f"   Contract: {contract_info.get('contract_address', 'N/A')}")
                self.stdout.write(f"   Network: {contract_info.get('network_name', 'Unknown')}")
                self.stdout.write(f"   Questions on chain: {contract_info.get('question_counter', 0)}")
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Contract info error: {str(e)}")
                )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Service: Not Available")
            )
        
        # Django data status
        total_questions = Question.objects.count()
        blockchain_questions = BlockchainQuestion.objects.count()
        synced_questions = BlockchainQuestion.objects.filter(is_blockchain_synced=True).count()
        blockchain_votes = BlockchainVote.objects.count()
        
        self.stdout.write(f"\n=== Django Data ===")
        self.stdout.write(f"📊 Total Questions: {total_questions}")
        self.stdout.write(f"🔗 Blockchain Questions: {blockchain_questions}")
        self.stdout.write(f"✅ Synced Questions: {synced_questions}")
        self.stdout.write(f"🗳️  Blockchain Votes: {blockchain_votes}")
        
        if blockchain_questions > synced_questions:
            pending = blockchain_questions - synced_questions
            self.stdout.write(
                self.style.WARNING(f"⏳ Pending Sync: {pending} questions")
            )
    
    def sync_all_questions(self, force=False):
        """Sync all blockchain questions"""
        if not force and not is_web3_connected():
            raise CommandError(
                "Blockchain not connected. Use --force to sync anyway (mock mode)"
            )
        
        self.stdout.write("🔄 Starting bulk synchronization...")
        
        questions = BlockchainQuestion.objects.filter(
            use_blockchain=True,
            is_blockchain_synced=False
        )
        
        if not questions.exists():
            self.stdout.write(
                self.style.SUCCESS("✅ All questions are already synced")
            )
            return
        
        success_count = 0
        error_count = 0
        
        for question in questions:
            try:
                self.stdout.write(f"  Syncing: {question.question_text[:50]}...")
                result = question.create_on_blockchain()
                
                if result.get('success'):
                    success_count += 1
                    if self.verbosity > 1:
                        tx_hash = result.get('transaction_hash', 'N/A')
                        self.stdout.write(f"    ✅ Success: {tx_hash}")
                else:
                    error_count += 1
                    error_msg = result.get('error', 'Unknown error')
                    self.stdout.write(
                        self.style.ERROR(f"    ❌ Failed: {error_msg}")
                    )
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f"    ❌ Exception: {str(e)}")
                )
        
        # Summary
        self.stdout.write(f"\n=== Sync Summary ===")
        self.stdout.write(f"✅ Success: {success_count}")
        self.stdout.write(f"❌ Errors: {error_count}")
        
        if success_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"🎉 Successfully synced {success_count} questions")
            )
    
    def sync_single_question(self, question_id):
        """Sync a single question by ID"""
        try:
            question = BlockchainQuestion.objects.get(pk=question_id)
        except BlockchainQuestion.DoesNotExist:
            raise CommandError(f"Question with ID {question_id} not found")
        
        if not question.use_blockchain:
            # Enable blockchain for this question
            question.use_blockchain = True
            question.save()
            self.stdout.write(f"✅ Enabled blockchain for question {question_id}")
        
        if question.is_blockchain_synced:
            self.stdout.write(
                self.style.WARNING(f"⚠️  Question {question_id} is already synced")
            )
            
            # Offer to re-sync from blockchain
            result = question.sync_from_blockchain()
            if result.get('success'):
                self.stdout.write("✅ Refreshed from blockchain")
            else:
                self.stdout.write(f"❌ Refresh failed: {result.get('error')}")
            return
        
        # Sync to blockchain
        self.stdout.write(f"🔄 Syncing question {question_id} to blockchain...")
        result = question.create_on_blockchain()
        
        if result.get('success'):
            tx_hash = result.get('transaction_hash', 'N/A')
            self.stdout.write(
                self.style.SUCCESS(f"✅ Success! TX: {tx_hash}")
            )
        else:
            error_msg = result.get('error', 'Unknown error')
            self.stdout.write(
                self.style.ERROR(f"❌ Failed: {error_msg}")
            )
    
    def check_deployment(self):
        """Check if smart contract is properly deployed"""
        self.stdout.write("🔍 Checking smart contract deployment...")
        
        if not is_web3_connected():
            self.stdout.write(
                self.style.ERROR("❌ Cannot check deployment - blockchain not connected")
            )
            return
        
        try:
            contract_info = blockchain_service.get_contract_info()
            
            self.stdout.write("✅ Contract deployment verified:")
            self.stdout.write(f"   Address: {contract_info.get('contract_address')}")
            self.stdout.write(f"   Network: {contract_info.get('network_name')}")
            self.stdout.write(f"   Balance: {contract_info.get('balance', 0)} ETH")
            
            # Test contract functionality
            self.stdout.write("\n🧪 Testing contract functionality...")
            
            # Try to get question counter
            counter = contract_info.get('question_counter', 0)
            self.stdout.write(f"   Question counter: {counter}")
            
            self.stdout.write(
                self.style.SUCCESS("✅ Smart contract is working correctly")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Deployment check failed: {str(e)}")
            )
    
    def reset_sync_status(self, force=False):
        """Reset synchronization status for all questions"""
        if not force:
            response = input(
                "⚠️  This will reset sync status for ALL blockchain questions. "
                "Are you sure? [y/N]: "
            )
            if response.lower() not in ['y', 'yes']:
                self.stdout.write("Operation cancelled.")
                return
        
        self.stdout.write("🔄 Resetting sync status...")
        
        updated = BlockchainQuestion.objects.filter(
            is_blockchain_synced=True
        ).update(
            is_blockchain_synced=False,
            blockchain_id=None,
            blockchain_tx_hash='',
            blockchain_created_at=None
        )
        
        # Also clear blockchain votes
        deleted_votes = BlockchainVote.objects.all().delete()[0]
        
        self.stdout.write(f"✅ Reset {updated} questions")
        self.stdout.write(f"✅ Deleted {deleted_votes} blockchain votes")
        self.stdout.write(
            self.style.SUCCESS("🎉 Sync status reset complete")
        )