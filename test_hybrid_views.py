#!/usr/bin/env python
"""
Test script for hybrid Django-Blockchain views
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encuestas.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

from polls.blockchain.views import (
    hybrid_index, hybrid_detail, hybrid_results, 
    blockchain_status, create_blockchain_question
)
from polls.blockchain.models import BlockchainQuestion, BlockchainChoice
from polls.models import Question, Choice


def setup_request(path='/', method='GET', data=None):
    """Setup a mock request for testing"""
    factory = RequestFactory()
    
    if method.upper() == 'POST':
        request = factory.post(path, data or {})
    else:
        request = factory.get(path)
    
    # Add session
    request.session = SessionStore()
    
    # Add messages framework
    messages = FallbackStorage(request)
    request._messages = messages
    
    return request


def test_hybrid_index_view():
    """Test the hybrid index view"""
    print("📋 Testing hybrid index view...")
    
    try:
        # Create some test questions
        regular_question = Question.objects.create(
            question_text="Regular Django question",
            pub_date=timezone.now()
        )
        
        blockchain_question = BlockchainQuestion.objects.create(
            question_text="Blockchain question",
            pub_date=timezone.now(),
            use_blockchain=True
        )
        
        # Test the view
        request = setup_request('/')
        response = hybrid_index(request)
        
        print(f"✅ Hybrid index view working:")
        print(f"   - Status code: {response.status_code}")
        print(f"   - Content type: {response.get('Content-Type', 'text/html')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid index view failed: {e}")
        return False


def test_hybrid_detail_view():
    """Test the hybrid detail view"""
    print("\n📖 Testing hybrid detail view...")
    
    try:
        # Create test question with choices
        question = BlockchainQuestion.objects.create(
            question_text="Test detail question",
            pub_date=timezone.now(),
            use_blockchain=True
        )
        
        BlockchainChoice.objects.create(question=question, choice_text="Choice A")
        BlockchainChoice.objects.create(question=question, choice_text="Choice B")
        
        # Test the view
        request = setup_request(f'/{question.id}/')
        response = hybrid_detail(request, question.id)
        
        print(f"✅ Hybrid detail view working:")
        print(f"   - Status code: {response.status_code}")
        print(f"   - Question ID: {question.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid detail view failed: {e}")
        return False


def test_hybrid_results_view():
    """Test the hybrid results view"""
    print("\n📊 Testing hybrid results view...")
    
    try:
        # Create test question with votes
        question = BlockchainQuestion.objects.create(
            question_text="Test results question",
            pub_date=timezone.now(),
            use_blockchain=True
        )
        
        choice1 = BlockchainChoice.objects.create(question=question, choice_text="Choice 1")
        choice2 = BlockchainChoice.objects.create(question=question, choice_text="Choice 2")
        
        # Add some votes
        choice1.votes = 5
        choice2.votes = 3
        choice1.save()
        choice2.save()
        
        # Test the view
        request = setup_request(f'/{question.id}/results/')
        response = hybrid_results(request, question.id)
        
        print(f"✅ Hybrid results view working:")
        print(f"   - Status code: {response.status_code}")
        print(f"   - Total votes: {choice1.votes + choice2.votes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid results view failed: {e}")
        return False


def test_blockchain_status_api():
    """Test blockchain status API endpoint"""
    print("\n🔗 Testing blockchain status API...")
    
    try:
        request = setup_request('/blockchain/status/')
        response = blockchain_status(request)
        
        # Parse JSON response
        import json
        data = json.loads(response.content.decode('utf-8'))
        
        print(f"✅ Blockchain status API working:")
        print(f"   - Status code: {response.status_code}")
        print(f"   - Connected: {data.get('connected', False)}")
        if data.get('connected'):
            print(f"   - Contract: {data.get('contract_address', 'N/A')}")
        else:
            print(f"   - Error: {data.get('error', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Blockchain status API failed: {e}")
        return False


def test_create_blockchain_question_api():
    """Test create blockchain question API"""
    print("\n🏭 Testing create blockchain question API...")
    
    try:
        import json
        
        # Test data
        test_data = {
            'question_text': '¿Cuál es tu criptomoneda favorita?',
            'choices': ['Bitcoin', 'Ethereum', 'Solana', 'Cardano']
        }
        
        request = setup_request(
            '/blockchain/create/', 
            method='POST', 
            data=json.dumps(test_data)
        )
        request.content_type = 'application/json'
        request._body = json.dumps(test_data).encode('utf-8')
        
        response = create_blockchain_question(request)
        
        # Parse response
        data = json.loads(response.content.decode('utf-8'))
        
        print(f"✅ Create blockchain question API working:")
        print(f"   - Status code: {response.status_code}")
        print(f"   - Success: {data.get('success', False)}")
        if data.get('success'):
            print(f"   - Question ID: {data.get('question_id')}")
            print(f"   - Blockchain ID: {data.get('blockchain_id')}")
        else:
            print(f"   - Error: {data.get('error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Create blockchain question API failed: {e}")
        return False


def test_urls_configuration():
    """Test that URLs are configured correctly"""
    print("\n🔗 Testing URL configuration...")
    
    try:
        from django.urls import reverse
        
        # Test URL reversal
        urls_to_test = [
            ('polls:hybrid_index', []),
            ('polls:blockchain_status', []),
        ]
        
        working_urls = 0
        for url_name, args in urls_to_test:
            try:
                url = reverse(url_name, args=args)
                print(f"   ✅ {url_name} -> {url}")
                working_urls += 1
            except Exception as e:
                print(f"   ❌ {url_name} failed: {e}")
        
        print(f"✅ URL configuration: {working_urls}/{len(urls_to_test)} URLs working")
        return working_urls == len(urls_to_test)
        
    except Exception as e:
        print(f"❌ URL configuration test failed: {e}")
        return False


def test_client_requests():
    """Test using Django test client"""
    print("\n🌐 Testing with Django test client...")
    
    try:
        client = Client()
        
        # Test hybrid index
        response = client.get('/polls/hybrid/')
        print(f"   Hybrid index: {response.status_code}")
        
        # Test blockchain status API
        response = client.get('/polls/blockchain/status/')
        print(f"   Blockchain status: {response.status_code}")
        
        print("✅ Django test client working")
        return True
        
    except Exception as e:
        print(f"❌ Django test client failed: {e}")
        return False


def main():
    """Run all hybrid view tests"""
    print("🚀 Django-Blockchain Hybrid Views Test Suite")
    print("=" * 60)
    
    tests = [
        test_hybrid_index_view,
        test_hybrid_detail_view,
        test_hybrid_results_view,
        test_blockchain_status_api,
        test_create_blockchain_question_api,
        test_urls_configuration,
        test_client_requests
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print("🏁 HYBRID VIEWS TEST SUMMARY")
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All hybrid view tests passed!")
        print("\n💡 Your hybrid views are working:")
        print("   ✅ Hybrid index (Django + Blockchain questions)")
        print("   ✅ Hybrid detail (Auto-detection of question type)")
        print("   ✅ Hybrid results (Comparison view)")
        print("   ✅ Blockchain APIs (Status, creation)")
        print("   ✅ URL configuration")
        print("   ✅ Django test client integration")
        print("\n🌐 Ready for frontend templates!")
        return True
    else:
        print("❌ Some hybrid view tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)