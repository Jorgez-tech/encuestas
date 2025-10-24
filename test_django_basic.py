#!/usr/bin/env python
"""
Basic test to verify Django setup and blockchain module loading
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encuestas.settings')
django.setup()

def test_django_setup():
    """Test basic Django setup"""
    print("🔧 Testing Django setup...")
    
    try:
        from django.conf import settings
        print(f"✅ Django configured with SECRET_KEY: {settings.SECRET_KEY[:10]}...")
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_blockchain_module():
    """Test blockchain module import"""
    print("\n📦 Testing blockchain module import...")
    
    try:
        from polls.blockchain import config, services
        print("✅ Blockchain modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Blockchain module import failed: {e}")
        return False

def test_web3_imports():
    """Test Web3 dependencies"""
    print("\n🌐 Testing Web3 dependencies...")
    
    try:
        from web3 import Web3
        from eth_account import Account
        print("✅ Web3 dependencies available")
        return True
    except Exception as e:
        print(f"❌ Web3 dependencies failed: {e}")
        return False

def test_django_models():
    """Test Django models"""
    print("\n📊 Testing Django models...")
    
    try:
        from polls.models import Question, Choice
        
        # Test creating a question
        question = Question(question_text="Test Question", pub_date=django.utils.timezone.now())
        print(f"✅ Django models working: {question.question_text}")
        return True
    except Exception as e:
        print(f"❌ Django models failed: {e}")
        return False

def test_blockchain_config():
    """Test blockchain configuration"""
    print("\n⚙️  Testing blockchain configuration...")
    
    try:
        from polls.blockchain.config import VOTING_CONTRACT_ADDRESS, VOTING_CONTRACT_ABI, USE_MOCK_BLOCKCHAIN
        
        print(f"✅ Blockchain config loaded:")
        print(f"   - Contract Address: {VOTING_CONTRACT_ADDRESS}")
        print(f"   - ABI Functions: {len([x for x in VOTING_CONTRACT_ABI if x.get('type') == 'function'])}")
        print(f"   - Mock Mode: {USE_MOCK_BLOCKCHAIN}")
        return True
    except Exception as e:
        print(f"❌ Blockchain config failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🚀 Django + Blockchain Basic Setup Test")
    print("=" * 45)
    
    tests = [
        test_django_setup,
        test_blockchain_module,
        test_web3_imports, 
        test_django_models,
        test_blockchain_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 45)
    print("🏁 BASIC SETUP SUMMARY")
    print(f"✅ Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 Basic setup is working! Ready for blockchain integration.")
        print("\n💡 Next steps:")
        print("   1. Start Hardhat Network: 'npx hardhat node'")
        print("   2. Deploy contract: 'npx hardhat ignition deploy ...'")
        print("   3. Set USE_MOCK_BLOCKCHAIN=False")
        print("   4. Run full integration tests")
        return True
    else:
        print("❌ Some basic setup issues found. Fix these first.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)