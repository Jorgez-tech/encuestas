#!/usr/bin/env python
"""
Test script for Django + Web3 integration
Run this to verify that Django can connect to blockchain and interact with smart contract
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encuestas.settings')
django.setup()

from polls.blockchain.services import blockchain_service
from polls.blockchain.config import is_web3_connected, get_contract


def test_web3_connection():
    """Test basic Web3 connection"""
    print("🔗 Testing Web3 connection...")
    
    if is_web3_connected():
        print("✅ Web3 connected successfully!")
        return True
    else:
        print("❌ Web3 connection failed!")
        return False


def test_contract_connection():
    """Test smart contract connection"""
    print("\n📋 Testing smart contract connection...")
    
    contract = get_contract()
    if contract:
        print(f"✅ Contract connected at: {contract.address}")
        return True
    else:
        print("❌ Contract connection failed!")
        return False


def test_contract_info():
    """Test getting contract information"""
    print("\n📊 Testing contract info...")
    
    info = blockchain_service.get_contract_info()
    if "error" not in info:
        print(f"✅ Contract info retrieved:")
        print(f"   - Address: {info['contract_address']}")
        print(f"   - Questions: {info['question_counter']}")
        print(f"   - Owner: {info['owner']}")
        return True
    else:
        print(f"❌ Contract info error: {info.get('error', 'Unknown error')}")
        return False


def test_create_question():
    """Test creating a question on blockchain"""
    print("\n🗳️  Testing question creation...")
    
    question_text = "¿Cuál es tu framework web favorito?"
    choices = ["Django", "Flask", "FastAPI", "React"]
    
    result = blockchain_service.create_question_on_blockchain(question_text, choices)
    
    if result.get("success"):
        print(f"✅ Question created successfully!")
        print(f"   - Transaction: {result['transaction_hash']}")
        print(f"   - Question ID: {result['question_id']}")
        print(f"   - Gas used: {result['gas_used']}")
        return result['question_id']
    else:
        print(f"❌ Question creation failed: {result.get('error', 'Unknown error')}")
        return None


def test_get_question(question_id):
    """Test getting question from blockchain"""
    print(f"\n📖 Testing get question {question_id}...")
    
    result = blockchain_service.get_question_from_blockchain(question_id)
    
    if result.get("success"):
        print(f"✅ Question retrieved:")
        print(f"   - Text: {result['question_text']}")
        print(f"   - Choices: {result['choices']}")
        print(f"   - Active: {result['is_active']}")
        print(f"   - Total votes: {result['total_votes']}")
        return True
    else:
        print(f"❌ Get question failed: {result.get('error', 'Unknown error')}")
        return False


def test_vote_on_question(question_id, choice_index=0):
    """Test voting on a question"""
    print(f"\n🗳️  Testing vote on question {question_id}, choice {choice_index}...")
    
    result = blockchain_service.vote_on_blockchain(question_id, choice_index)
    
    if result.get("success"):
        print(f"✅ Vote cast successfully!")
        print(f"   - Transaction: {result['transaction_hash']}")
        print(f"   - Gas used: {result['gas_used']}")
        return True
    else:
        print(f"❌ Voting failed: {result.get('error', 'Unknown error')}")
        return False


def test_get_results(question_id):
    """Test getting voting results"""
    print(f"\n📊 Testing get results for question {question_id}...")
    
    result = blockchain_service.get_vote_results_from_blockchain(question_id)
    
    if result.get("success"):
        print(f"✅ Results retrieved:")
        print(f"   - Question: {result['question_text']}")
        print(f"   - Total votes: {result['total_votes']}")
        print("   - Results:")
        for res in result['results']:
            print(f"     • {res['choice']}: {res['votes']} votes ({res['percentage']}%)")
        return True
    else:
        print(f"❌ Get results failed: {result.get('error', 'Unknown error')}")
        return False


def test_get_all_questions():
    """Test getting all questions"""
    print(f"\n📋 Testing get all questions...")
    
    result = blockchain_service.get_all_questions_from_blockchain()
    
    if result.get("success"):
        print(f"✅ All questions retrieved:")
        print(f"   - Total questions: {result['total_count']}")
        for i, q in enumerate(result['questions']):
            print(f"   - Question {i}: {q['question_text'][:50]}...")
        return True
    else:
        print(f"❌ Get all questions failed: {result.get('error', 'Unknown error')}")
        return False


def main():
    """Run all tests"""
    print("🚀 Django + Web3 Integration Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Web3 Connection
    total_tests += 1
    if test_web3_connection():
        tests_passed += 1
    
    # Test 2: Contract Connection
    total_tests += 1
    if test_contract_connection():
        tests_passed += 1
    
    # Test 3: Contract Info
    total_tests += 1
    if test_contract_info():
        tests_passed += 1
    
    # Test 4: Create Question
    total_tests += 1
    question_id = test_create_question()
    if question_id is not None:
        tests_passed += 1
        
        # Test 5: Get Question
        total_tests += 1
        if test_get_question(question_id):
            tests_passed += 1
        
        # Test 6: Vote on Question
        total_tests += 1
        if test_vote_on_question(question_id, 0):  # Vote for Django
            tests_passed += 1
        
        # Test 7: Get Results
        total_tests += 1
        if test_get_results(question_id):
            tests_passed += 1
    
    # Test 8: Get All Questions
    total_tests += 1
    if test_get_all_questions():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Django + Web3 integration is working!")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)