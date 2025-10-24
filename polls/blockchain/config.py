"""
Web3 Configuration for Django-Blockchain Integration
"""

from web3 import Web3
from django.conf import settings
import json
import os


# Hardhat local network configuration
HARDHAT_RPC_URL = "http://127.0.0.1:8545"  # Default Hardhat Network URL

# Contract deployment details (from our successful deployment)
VOTING_CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# For testing without external Hardhat node
USE_MOCK_BLOCKCHAIN = True  # Set to False when Hardhat Network is running

# Contract ABI (extracted from compiled Hardhat artifacts)
VOTING_CONTRACT_ABI = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"}
        ],
        "name": "OwnableInvalidOwner",
        "type": "error"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"}
        ],
        "name": "OwnableUnauthorizedAccount",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "ReentrancyGuardReentrantCall",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "previousOwner", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}
        ],
        "name": "OwnershipTransferred",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "questionId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "questionText", "type": "string"}
        ],
        "name": "QuestionCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "questionId", "type": "uint256"},
            {"indexed": True, "internalType": "uint256", "name": "choiceIndex", "type": "uint256"},
            {"indexed": True, "internalType": "address", "name": "voter", "type": "address"}
        ],
        "name": "VoteCast",
        "type": "event"
    },
    {
        "inputs": [
            {"internalType": "string", "name": "_questionText", "type": "string"},
            {"internalType": "string[]", "name": "_choices", "type": "string[]"}
        ],
        "name": "createQuestion",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_questionId", "type": "uint256"}
        ],
        "name": "getQuestion",
        "outputs": [
            {"internalType": "string", "name": "questionText", "type": "string"},
            {"internalType": "string[]", "name": "choices", "type": "string[]"},
            {"internalType": "bool", "name": "isActive", "type": "bool"},
            {"internalType": "uint256", "name": "totalVotes", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_questionId", "type": "uint256"},
            {"internalType": "uint256", "name": "_choiceIndex", "type": "uint256"}
        ],
        "name": "getVotes",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_user", "type": "address"},
            {"internalType": "uint256", "name": "_questionId", "type": "uint256"}
        ],
        "name": "hasUserVoted",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {"internalType": "address", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "questionCounter",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_questionId", "type": "uint256"},
            {"internalType": "bool", "name": "_isActive", "type": "bool"}
        ],
        "name": "setQuestionActive",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "_questionId", "type": "uint256"},
            {"internalType": "uint256", "name": "_choiceIndex", "type": "uint256"}
        ],
        "name": "vote",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]


class Web3Manager:
    """
    Singleton manager for Web3 connections and contract interactions
    """
    _instance = None
    _web3 = None
    _contract = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Web3Manager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._web3 is None:
            self._initialize_web3()
    
    def _initialize_web3(self):
        """Initialize Web3 connection"""
        try:
            if USE_MOCK_BLOCKCHAIN:
                print("⚠️  Using mock blockchain mode (Hardhat Network not required)")
                # For testing purposes, we'll simulate connection
                # In real scenario, you'd start Hardhat Network first
                self._web3 = None
                self._contract = None
                return
            
            # Connect to Hardhat local network
            self._web3 = Web3(Web3.HTTPProvider(HARDHAT_RPC_URL))
            
            # Verify connection
            if not self._web3.is_connected():
                raise ConnectionError("Unable to connect to Hardhat network")
            
            # Initialize contract
            self._contract = self._web3.eth.contract(
                address=VOTING_CONTRACT_ADDRESS,
                abi=VOTING_CONTRACT_ABI
            )
            
            print(f"✅ Web3 connected to Hardhat network")
            print(f"✅ Contract loaded at {VOTING_CONTRACT_ADDRESS}")
            
        except Exception as e:
            print(f"❌ Web3 initialization failed: {e}")
            print(f"💡 Tip: Start Hardhat Network with 'npx hardhat node' or set USE_MOCK_BLOCKCHAIN=True")
            self._web3 = None
            self._contract = None
    
    @property
    def web3(self):
        """Get Web3 instance"""
        return self._web3
    
    @property
    def contract(self):
        """Get contract instance"""
        return self._contract
    
    @property
    def is_connected(self):
        """Check if Web3 is connected"""
        return self._web3 is not None and self._web3.is_connected()
    
    def get_default_account(self):
        """Get the first account from Hardhat (usually the deployer)"""
        if self._web3:
            accounts = self._web3.eth.accounts
            return accounts[0] if accounts else None
        return None
    
    def get_account_balance(self, address):
        """Get balance of an account in ETH"""
        if self._web3:
            balance_wei = self._web3.eth.get_balance(address)
            return self._web3.from_wei(balance_wei, 'ether')
        return 0


# Global instance
web3_manager = Web3Manager()


def get_web3():
    """Get Web3 instance"""
    return web3_manager.web3


def get_contract():
    """Get VotingContract instance"""
    return web3_manager.contract


def is_web3_connected():
    """Check if Web3 is connected"""
    return web3_manager.is_connected