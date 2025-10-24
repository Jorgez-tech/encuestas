"""
Hybrid Django-Blockchain Views

These views handle both traditional Django questions and blockchain-enabled questions,
providing a seamless experience for users regardless of the backend storage.
"""

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator

from polls.models import Question as BaseQuestion, Choice as BaseChoice
from .models import BlockchainQuestion, BlockchainChoice, BlockchainVote
from .services import blockchain_service
from .config import is_web3_connected

import json
import logging

logger = logging.getLogger(__name__)


def hybrid_index(request):
    """
    Enhanced index view that shows both regular and blockchain questions
    """
    # Get all questions (both regular and blockchain)
    all_questions = []
    
    # Get regular Django questions
    regular_questions = BaseQuestion.objects.order_by('-pub_date')[:5]
    for q in regular_questions:
        all_questions.append({
            'question': q,
            'type': 'django',
            'is_blockchain': False,
            'is_synced': False,
            'blockchain_available': False
        })
    
    # Get blockchain questions
    blockchain_questions = BlockchainQuestion.objects.order_by('-pub_date')[:5]
    for q in blockchain_questions:
        all_questions.append({
            'question': q,
            'type': 'blockchain',
            'is_blockchain': q.use_blockchain,
            'is_synced': q.is_blockchain_synced,
            'blockchain_available': q.is_blockchain_available()
        })
    
    # Sort all questions by publication date
    all_questions.sort(key=lambda x: x['question'].pub_date, reverse=True)
    
    # Take only the latest 10
    latest_questions = all_questions[:10]
    
    context = {
        'latest_question_list': latest_questions,
        'blockchain_connected': is_web3_connected(),
        'blockchain_service_available': blockchain_service.is_available()
    }
    
    return render(request, 'polls/hybrid_index.html', context)


def hybrid_detail(request, question_id, question_type='auto'):
    """
    Enhanced detail view that handles both question types
    
    Args:
        question_id: ID of the question
        question_type: 'django', 'blockchain', or 'auto' (default)
    """
    question = None
    is_blockchain = False
    blockchain_info = {}
    
    # Try to determine question type and get question
    if question_type == 'blockchain':
        question = get_object_or_404(BlockchainQuestion, pk=question_id)
        is_blockchain = True
    elif question_type == 'django':
        question = get_object_or_404(BaseQuestion, pk=question_id)
        is_blockchain = False
    else:  # auto-detect
        # Try blockchain first, then regular
        try:
            question = BlockchainQuestion.objects.get(pk=question_id)
            is_blockchain = True
        except BlockchainQuestion.DoesNotExist:
            question = get_object_or_404(BaseQuestion, pk=question_id)
            is_blockchain = False
    
    # Get blockchain info if it's a blockchain question
    if is_blockchain and hasattr(question, 'use_blockchain'):
        blockchain_info = {
            'use_blockchain': question.use_blockchain,
            'is_synced': question.is_blockchain_synced,
            'blockchain_id': question.blockchain_id,
            'tx_hash': question.blockchain_tx_hash,
            'blockchain_available': question.is_blockchain_available()
        }
        
        # Check if user has voted on blockchain (mock check for now)
        blockchain_info['user_voted_blockchain'] = False
    
    context = {
        'question': question,
        'is_blockchain': is_blockchain,
        'blockchain_info': blockchain_info,
        'blockchain_connected': is_web3_connected()
    }
    
    return render(request, 'polls/hybrid_detail.html', context)


def hybrid_vote(request, question_id, question_type='auto'):
    """
    Enhanced vote view that handles both Django and blockchain voting
    """
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('polls:hybrid_detail', args=(question_id,)))
    
    # Get the question (similar logic to hybrid_detail)
    question = None
    is_blockchain = False
    
    if question_type == 'blockchain':
        question = get_object_or_404(BlockchainQuestion, pk=question_id)
        is_blockchain = True
    elif question_type == 'django':
        question = get_object_or_404(BaseQuestion, pk=question_id)
        is_blockchain = False
    else:  # auto-detect
        try:
            question = BlockchainQuestion.objects.get(pk=question_id)
            is_blockchain = True
        except BlockchainQuestion.DoesNotExist:
            question = get_object_or_404(BaseQuestion, pk=question_id)
            is_blockchain = False
    
    # Get selected choice
    try:
        choice_id = request.POST['choice']
        selected_choice = question.choice_set.get(pk=choice_id)
    except (KeyError, BaseChoice.DoesNotExist):
        return render(request, 'polls/hybrid_detail.html', {
            'question': question,
            'is_blockchain': is_blockchain,
            'error_message': "No seleccionaste una opción válida.",
        })
    
    # Handle voting based on question type
    vote_method = request.POST.get('vote_method', 'django')  # Default to Django voting
    
    if is_blockchain and vote_method == 'blockchain' and hasattr(question, 'use_blockchain'):
        # Blockchain voting
        success = handle_blockchain_vote(request, question, selected_choice)
        if success:
            messages.success(request, '¡Tu voto ha sido registrado en blockchain! 🔗')
        else:
            messages.error(request, 'Error al registrar el voto en blockchain. Se registró en Django.')
            # Fall back to Django voting
            selected_choice.votes += 1
            selected_choice.save()
            messages.info(request, 'Voto registrado en Django como respaldo.')
    else:
        # Traditional Django voting
        selected_choice.votes += 1
        selected_choice.save()
        messages.success(request, '¡Tu voto ha sido registrado correctamente! 💾')
    
    return HttpResponseRedirect(reverse('polls:hybrid_results', args=(question.id,)))


def handle_blockchain_vote(request, question, selected_choice):
    """
    Handle blockchain voting logic
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if not question.is_blockchain_available():
            logger.warning("Blockchain not available for voting")
            return False
        
        # Find choice index
        choices = list(question.choice_set.all())
        choice_index = None
        
        for i, choice in enumerate(choices):
            if choice.id == selected_choice.id:
                choice_index = i
                break
        
        if choice_index is None:
            logger.error("Could not find choice index for blockchain voting")
            return False
        
        # For now, we'll simulate the vote since we need actual wallet connection
        # In real implementation, you'd get the user's wallet address
        mock_voter_address = "0x742d35Cc6634C0532925a3b8D2c4d9FD4e4AD0DB"
        
        result = question.vote_on_blockchain(choice_index, mock_voter_address)
        
        if result.get('success'):
            # Record the vote locally for reference
            BlockchainVote.objects.create(
                question=question,
                choice_index=choice_index,
                voter_address=mock_voter_address,
                transaction_hash=result.get('transaction_hash', 'mock_tx')
            )
            logger.info(f"Blockchain vote recorded: {result}")
            return True
        else:
            logger.error(f"Blockchain vote failed: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"Error handling blockchain vote: {e}")
        return False


def hybrid_results(request, question_id, question_type='auto'):
    """
    Enhanced results view that shows both Django and blockchain results
    """
    question = None
    is_blockchain = False
    
    # Get question (similar logic as before)
    if question_type == 'blockchain':
        question = get_object_or_404(BlockchainQuestion, pk=question_id)
        is_blockchain = True
    elif question_type == 'django':
        question = get_object_or_404(BaseQuestion, pk=question_id)
        is_blockchain = False
    else:  # auto-detect
        try:
            question = BlockchainQuestion.objects.get(pk=question_id)
            is_blockchain = True
        except BlockchainQuestion.DoesNotExist:
            question = get_object_or_404(BaseQuestion, pk=question_id)
            is_blockchain = False
    
    # Get Django results
    choices = question.choice_set.all()
    total_votes = sum(choice.votes for choice in choices)
    
    django_results = []
    for choice in choices:
        percentage = (choice.votes / total_votes * 100) if total_votes > 0 else 0
        django_results.append({
            'choice': choice,
            'votes': choice.votes,
            'percentage': round(percentage, 1)
        })
    
    # Get blockchain results if available
    blockchain_results = None
    blockchain_total = 0
    
    if is_blockchain and hasattr(question, 'is_blockchain_synced') and question.is_blockchain_synced:
        blockchain_data = question.get_blockchain_results()
        if blockchain_data.get('success'):
            blockchain_results = blockchain_data.get('results', [])
            blockchain_total = blockchain_data.get('total_votes', 0)
    
    context = {
        'question': question,
        'is_blockchain': is_blockchain,
        'django_results': django_results,
        'django_total': total_votes,
        'blockchain_results': blockchain_results,
        'blockchain_total': blockchain_total,
        'blockchain_connected': is_web3_connected(),
        'show_comparison': blockchain_results is not None
    }
    
    return render(request, 'polls/hybrid_results.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_blockchain_question(request):
    """
    API endpoint to create a question on blockchain
    """
    try:
        data = json.loads(request.body)
        question_text = data.get('question_text')
        choices = data.get('choices', [])
        
        if not question_text or len(choices) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Question text and at least 2 choices required'
            })
        
        # Create blockchain question
        question = BlockchainQuestion.objects.create_with_blockchain(
            question_text=question_text,
            choices=choices,
            use_blockchain=True
        )
        
        return JsonResponse({
            'success': True,
            'question_id': question.id,
            'blockchain_id': question.blockchain_id,
            'is_synced': question.is_blockchain_synced
        })
        
    except Exception as e:
        logger.error(f"Error creating blockchain question: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def blockchain_status(request):
    """
    API endpoint to check blockchain connection status
    """
    if blockchain_service.is_available():
        contract_info = blockchain_service.get_contract_info()
        return JsonResponse({
            'connected': True,
            'contract_address': contract_info.get('contract_address'),
            'question_counter': contract_info.get('question_counter'),
            'owner': contract_info.get('owner')
        })
    else:
        return JsonResponse({
            'connected': False,
            'error': 'Blockchain service not available'
        })


def sync_question_to_blockchain(request, question_id):
    """
    Manual sync of existing question to blockchain
    """
    try:
        question = get_object_or_404(BlockchainQuestion, pk=question_id)
        
        if question.is_blockchain_synced:
            return JsonResponse({
                'success': False,
                'error': 'Question already synced to blockchain'
            })
        
        # Enable blockchain and create
        question.use_blockchain = True
        question.save()
        
        result = question.create_on_blockchain()
        
        return JsonResponse({
            'success': result.get('success', False),
            'transaction_hash': result.get('transaction_hash'),
            'blockchain_id': result.get('question_id'),
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"Error syncing question to blockchain: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })