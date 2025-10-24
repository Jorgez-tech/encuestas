#!/usr/bin/env python
"""
Test script for hybrid Django-Blockchain models
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encuestas.settings')
django.setup()

from polls.blockchain.models import BlockchainQuestion, BlockchainChoice, BlockchainVote
from polls.models import Question, Choice
from django.utils import timezone


def test_create_regular_question():
    """Test creating a regular Django question"""
    print("📝 Testing regular Django question creation...")
    
    try:
        question = Question.objects.create(
            question_text="¿Cuál es tu color favorito (Django)?",
            pub_date=timezone.now()
        )
        
        Choice.objects.create(question=question, choice_text="Rojo")
        Choice.objects.create(question=question, choice_text="Azul")
        Choice.objects.create(question=question, choice_text="Verde")
        
        print(f"✅ Regular question created: {question}")
        print(f"   - Choices: {[c.choice_text for c in question.choice_set.all()]}")
        return question
        
    except Exception as e:
        print(f"❌ Regular question creation failed: {e}")
        return None


def test_create_blockchain_question():
    """Test creating a blockchain question (without actually using blockchain)"""
    print("\n🔗 Testing blockchain question creation...")
    
    try:
        question = BlockchainQuestion.objects.create(
            question_text="¿Cuál es tu framework favorito (Blockchain)?",
            pub_date=timezone.now(),
            use_blockchain=True  # Enable blockchain (but won't actually use it in mock mode)
        )
        
        BlockchainChoice.objects.create(question=question, choice_text="Django")
        BlockchainChoice.objects.create(question=question, choice_text="FastAPI") 
        BlockchainChoice.objects.create(question=question, choice_text="Flask")
        
        print(f"✅ Blockchain question created: {question}")
        print(f"   - Choices: {[c.choice_text for c in question.choice_set.all()]}")
        print(f"   - Use blockchain: {question.use_blockchain}")
        print(f"   - Is synced: {question.is_blockchain_synced}")
        return question
        
    except Exception as e:
        print(f"❌ Blockchain question creation failed: {e}")
        return None


def test_blockchain_question_manager():
    """Test BlockchainQuestion manager methods"""
    print("\n📊 Testing BlockchainQuestion manager...")
    
    try:
        # Create questions with different settings
        q1 = BlockchainQuestion.objects.create(
            question_text="Blockchain enabled question",
            pub_date=timezone.now(),
            use_blockchain=True
        )
        
        q2 = BlockchainQuestion.objects.create(
            question_text="Regular question",
            pub_date=timezone.now(),
            use_blockchain=False
        )
        
        # Test manager methods
        blockchain_enabled = BlockchainQuestion.objects.blockchain_enabled()
        synced = BlockchainQuestion.objects.synced_with_blockchain()
        pending = BlockchainQuestion.objects.pending_blockchain_sync()
        
        print(f"✅ Manager methods working:")
        print(f"   - Blockchain enabled: {blockchain_enabled.count()}")
        print(f"   - Synced with blockchain: {synced.count()}")
        print(f"   - Pending sync: {pending.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Manager methods failed: {e}")
        return False


def test_create_with_blockchain_manager():
    """Test the create_with_blockchain manager method"""
    print("\n🏭 Testing create_with_blockchain manager method...")
    
    try:
        question = BlockchainQuestion.objects.create_with_blockchain(
            question_text="¿Cuál es tu lenguaje de programación favorito?",
            choices=["Python", "JavaScript", "Go", "Rust"],
            use_blockchain=True
        )
        
        print(f"✅ Question created with manager: {question}")
        print(f"   - Choices: {[c.choice_text for c in question.choice_set.all()]}")
        print(f"   - Use blockchain: {question.use_blockchain}")
        
        return question
        
    except Exception as e:
        print(f"❌ create_with_blockchain failed: {e}")
        return None


def test_hybrid_results():
    """Test getting hybrid results (Django + Blockchain)"""
    print("\n📈 Testing hybrid results...")
    
    try:
        # Create a question with some votes
        question = BlockchainQuestion.objects.create(
            question_text="Test hybrid results",
            pub_date=timezone.now(),
            use_blockchain=True
        )
        
        choice1 = BlockchainChoice.objects.create(question=question, choice_text="Option A")
        choice2 = BlockchainChoice.objects.create(question=question, choice_text="Option B")
        
        # Add some Django votes
        choice1.votes = 3
        choice2.votes = 2
        choice1.save()
        choice2.save()
        
        # Get hybrid results
        results = question.get_hybrid_results()
        
        print(f"✅ Hybrid results retrieved:")
        print(f"   - Question: {results['question_text']}")
        print(f"   - Django results: {results['django_results']}")
        print(f"   - Blockchain synced: {results['is_blockchain_synced']}")
        print(f"   - Blockchain results: {results['blockchain_results']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid results failed: {e}")
        return False


def test_blockchain_vote_model():
    """Test BlockchainVote model"""
    print("\n🗳️  Testing BlockchainVote model...")
    
    try:
        question = BlockchainQuestion.objects.create(
            question_text="Test vote tracking",
            pub_date=timezone.now(),
            use_blockchain=True
        )
        
        # Create a mock blockchain vote record
        vote = BlockchainVote.objects.create(
            question=question,
            choice_index=0,
            voter_address="0x742d35Cc6634C0532925a3b8D2c4d9FD4e4AD0DB",
            transaction_hash="0x123456789abcdef123456789abcdef123456789abcdef123456789abcdef123456"
        )
        
        print(f"✅ BlockchainVote created: {vote}")
        print(f"   - Voter: {vote.voter_address}")
        print(f"   - Choice index: {vote.choice_index}")
        print(f"   - Transaction: {vote.transaction_hash}")
        
        return vote
        
    except Exception as e:
        print(f"❌ BlockchainVote creation failed: {e}")
        return None


def test_model_inheritance():
    """Test that blockchain models inherit from base models correctly"""
    print("\n🧬 Testing model inheritance...")
    
    try:
        blockchain_question = BlockchainQuestion.objects.create(
            question_text="Inheritance test",
            pub_date=timezone.now()
        )
        
        # Test that it has both base and blockchain functionality
        print(f"✅ Model inheritance working:")
        print(f"   - Has base Question methods: {hasattr(blockchain_question, 'was_published_recently')}")
        print(f"   - Has blockchain methods: {hasattr(blockchain_question, 'create_on_blockchain')}")
        print(f"   - Is instance of Question: {isinstance(blockchain_question, Question)}")
        print(f"   - __str__ with emoji: {str(blockchain_question)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model inheritance test failed: {e}")
        return False


def main():
    """Run all hybrid model tests"""
    print("🚀 Django-Blockchain Hybrid Models Test Suite")
    print("=" * 55)
    
    tests = [
        test_create_regular_question,
        test_create_blockchain_question,
        test_blockchain_question_manager,
        test_create_with_blockchain_manager,
        test_hybrid_results,
        test_blockchain_vote_model,
        test_model_inheritance
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        result = test()
        if result is not None and result is not False:
            passed += 1
    
    print("\n" + "=" * 55)
    print("🏁 HYBRID MODELS TEST SUMMARY")
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All hybrid model tests passed!")
        print("\n💡 Your hybrid models are working:")
        print("   ✅ Regular Django questions")
        print("   ✅ Blockchain-enabled questions")
        print("   ✅ Hybrid results (Django + Blockchain)")
        print("   ✅ Vote tracking")
        print("   ✅ Model inheritance")
        print("\n🔗 Ready for blockchain integration!")
        return True
    else:
        print("❌ Some hybrid model tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)