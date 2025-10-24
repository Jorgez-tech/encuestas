"""
Advanced Django Admin for Blockchain Models

This admin interface provides comprehensive management of blockchain-enabled
questions, votes, and synchronization with smart contracts.
"""

from django.contrib import admin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum

from .models import BlockchainQuestion, BlockchainChoice, BlockchainVote
from .services import blockchain_service
from .config import is_web3_connected

import logging

logger = logging.getLogger(__name__)


class BlockchainChoiceInline(admin.TabularInline):
    """Inline admin for BlockchainChoice"""
    model = BlockchainChoice
    extra = 2
    fields = ('choice_text', 'votes')
    readonly_fields = ('votes',)


class BlockchainVoteInline(admin.TabularInline):
    """Inline admin for BlockchainVote (readonly)"""
    model = BlockchainVote
    extra = 0
    readonly_fields = ('voter_address', 'choice_index', 'transaction_hash', 'timestamp')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BlockchainQuestion)
class BlockchainQuestionAdmin(admin.ModelAdmin):
    """
    Advanced admin for BlockchainQuestion with Web3 integration
    """
    
    fieldsets = [
        ('Question Information', {
            'fields': ['question_text', 'pub_date']
        }),
        ('Blockchain Configuration', {
            'fields': ['use_blockchain', 'blockchain_id', 'blockchain_tx_hash', 'is_blockchain_synced'],
            'classes': ['collapse']
        }),
        ('Blockchain Status', {
            'fields': ['blockchain_created_at'],
            'classes': ['collapse']
        })
    ]
    
    inlines = [BlockchainChoiceInline, BlockchainVoteInline]
    
    list_display = [
        'question_text_with_status', 
        'pub_date', 
        'use_blockchain',
        'blockchain_status',
        'total_django_votes',
        'blockchain_actions'
    ]
    
    list_filter = [
        'use_blockchain', 
        'is_blockchain_synced', 
        'pub_date',
        'blockchain_created_at'
    ]
    
    search_fields = ['question_text', 'blockchain_tx_hash']
    
    readonly_fields = [
        'blockchain_id', 
        'blockchain_tx_hash', 
        'is_blockchain_synced', 
        'blockchain_created_at'
    ]
    
    actions = [
        'sync_to_blockchain',
        'sync_from_blockchain', 
        'check_blockchain_status'
    ]
    
    def get_urls(self):
        """Add custom URLs for blockchain operations"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/sync-to-blockchain/',
                self.admin_site.admin_view(self.sync_to_blockchain_view),
                name='polls_blockchainquestion_sync_to_blockchain',
            ),
            path(
                '<path:object_id>/sync-from-blockchain/',
                self.admin_site.admin_view(self.sync_from_blockchain_view),
                name='polls_blockchainquestion_sync_from_blockchain',
            ),
            path(
                'blockchain-dashboard/',
                self.admin_site.admin_view(self.blockchain_dashboard_view),
                name='polls_blockchain_dashboard',
            ),
        ]
        return custom_urls + urls
    
    def question_text_with_status(self, obj):
        """Display question text with blockchain status emoji"""
        if obj.is_blockchain_synced:
            emoji = "🔗"
            title = "Synced with blockchain"
        elif obj.use_blockchain:
            emoji = "⏳"
            title = "Pending blockchain sync"
        else:
            emoji = "💾"
            title = "Django only"
        
        return format_html(
            '<span title="{}">{} {}</span>',
            title,
            emoji,
            obj.question_text[:50] + ('...' if len(obj.question_text) > 50 else '')
        )
    question_text_with_status.short_description = 'Question'
    question_text_with_status.admin_order_field = 'question_text'
    
    def blockchain_status(self, obj):
        """Display blockchain synchronization status"""
        if not obj.use_blockchain:
            return format_html('<span style="color: gray;">Not enabled</span>')
        
        if obj.is_blockchain_synced:
            return format_html(
                '<span style="color: green;">✓ Synced</span><br>'
                '<small>ID: {}</small>',
                obj.blockchain_id or 'N/A'
            )
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    blockchain_status.short_description = 'Blockchain Status'
    
    def total_django_votes(self, obj):
        """Display total votes in Django database"""
        total = sum(choice.votes for choice in obj.choice_set.all())
        return format_html('<strong>{}</strong>', total)
    total_django_votes.short_description = 'Django Votes'
    
    def blockchain_actions(self, obj):
        """Display action buttons for blockchain operations"""
        actions = []
        
        if not obj.use_blockchain:
            actions.append(
                '<span style="color: gray;">Blockchain disabled</span>'
            )
        elif not obj.is_blockchain_synced:
            sync_url = reverse(
                'admin:polls_blockchainquestion_sync_to_blockchain',
                args=[obj.pk]
            )
            actions.append(
                f'<a href="{sync_url}" class="button">📤 Sync to Blockchain</a>'
            )
        else:
            sync_url = reverse(
                'admin:polls_blockchainquestion_sync_from_blockchain',
                args=[obj.pk]
            )
            actions.append(
                f'<a href="{sync_url}" class="button">📥 Sync from Blockchain</a>'
            )
            
            if obj.blockchain_tx_hash:
                actions.append(
                    f'<br><small>TX: {obj.blockchain_tx_hash[:10]}...</small>'
                )
        
        return format_html('<br>'.join(actions))
    blockchain_actions.short_description = 'Actions'
    blockchain_actions.allow_tags = True
    
    def sync_to_blockchain(self, request, queryset):
        """Admin action to sync questions to blockchain"""
        if not is_web3_connected():
            self.message_user(
                request,
                "Blockchain not connected. Cannot sync questions.",
                level=messages.ERROR
            )
            return
        
        success_count = 0
        for question in queryset:
            if not question.use_blockchain:
                question.use_blockchain = True
                question.save()
            
            if not question.is_blockchain_synced:
                result = question.create_on_blockchain()
                if result.get('success'):
                    success_count += 1
        
        if success_count > 0:
            self.message_user(
                request,
                f"Successfully synced {success_count} question(s) to blockchain.",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "No questions were synced. Check blockchain connection.",
                level=messages.WARNING
            )
    sync_to_blockchain.short_description = "📤 Sync selected questions to blockchain"
    
    def sync_from_blockchain(self, request, queryset):
        """Admin action to sync questions from blockchain"""
        if not is_web3_connected():
            self.message_user(
                request,
                "Blockchain not connected. Cannot sync questions.",
                level=messages.ERROR
            )
            return
        
        success_count = 0
        for question in queryset:
            if question.is_blockchain_synced:
                result = question.sync_from_blockchain()
                if result.get('success'):
                    success_count += 1
        
        self.message_user(
            request,
            f"Checked {success_count} question(s) against blockchain.",
            level=messages.INFO
        )
    sync_from_blockchain.short_description = "📥 Sync selected questions from blockchain"
    
    def check_blockchain_status(self, request, queryset):
        """Admin action to check blockchain status"""
        if blockchain_service.is_available():
            contract_info = blockchain_service.get_contract_info()
            self.message_user(
                request,
                f"Blockchain connected. Contract: {contract_info.get('contract_address', 'N/A')}, "
                f"Questions: {contract_info.get('question_counter', 0)}",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "Blockchain service not available. Check connection.",
                level=messages.ERROR
            )
    check_blockchain_status.short_description = "🔗 Check blockchain connection"
    
    def sync_to_blockchain_view(self, request, object_id):
        """Custom view for syncing individual question to blockchain"""
        question = self.get_object(request, object_id)
        
        if not question:
            self.message_user(request, "Question not found.", level=messages.ERROR)
            return HttpResponseRedirect("../")
        
        if not is_web3_connected():
            self.message_user(request, "Blockchain not connected.", level=messages.ERROR)
            return HttpResponseRedirect("../")
        
        # Enable blockchain and sync
        question.use_blockchain = True
        question.save()
        
        result = question.create_on_blockchain()
        
        if result.get('success'):
            self.message_user(
                request,
                f"Question synced to blockchain! TX: {result.get('transaction_hash', 'N/A')}",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                f"Failed to sync to blockchain: {result.get('error', 'Unknown error')}",
                level=messages.ERROR
            )
        
        return HttpResponseRedirect("../")
    
    def sync_from_blockchain_view(self, request, object_id):
        """Custom view for syncing individual question from blockchain"""
        question = self.get_object(request, object_id)
        
        if not question or not question.is_blockchain_synced:
            self.message_user(request, "Question not synced with blockchain.", level=messages.ERROR)
            return HttpResponseRedirect("../")
        
        result = question.sync_from_blockchain()
        
        if result.get('success'):
            self.message_user(
                request,
                "Question data refreshed from blockchain.",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                f"Failed to sync from blockchain: {result.get('error', 'Unknown error')}",
                level=messages.ERROR
            )
        
        return HttpResponseRedirect("../")
    
    def blockchain_dashboard_view(self, request):
        """Custom dashboard view for blockchain operations"""
        # Get statistics
        total_questions = BlockchainQuestion.objects.count()
        blockchain_enabled = BlockchainQuestion.objects.filter(use_blockchain=True).count()
        synced_questions = BlockchainQuestion.objects.filter(is_blockchain_synced=True).count()
        pending_sync = blockchain_enabled - synced_questions
        
        total_votes = BlockchainVote.objects.count()
        
        # Get blockchain service status
        blockchain_connected = is_web3_connected()
        contract_info = {}
        
        if blockchain_connected and blockchain_service.is_available():
            contract_info = blockchain_service.get_contract_info()
        
        context = {
            'title': 'Blockchain Dashboard',
            'stats': {
                'total_questions': total_questions,
                'blockchain_enabled': blockchain_enabled,
                'synced_questions': synced_questions,
                'pending_sync': pending_sync,
                'total_votes': total_votes,
            },
            'blockchain_connected': blockchain_connected,
            'contract_info': contract_info,
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/blockchain_dashboard.html', context)


@admin.register(BlockchainChoice)
class BlockchainChoiceAdmin(admin.ModelAdmin):
    """Admin for BlockchainChoice"""
    list_display = ['choice_text', 'question', 'votes', 'question_blockchain_status']
    list_filter = ['question']
    search_fields = ['choice_text', 'question__question_text']
    readonly_fields = ['votes']
    
    def question_blockchain_status(self, obj):
        """Show blockchain status of the parent question"""
        # Check if the question is a BlockchainQuestion instance
        try:
            if hasattr(obj.question, 'blockchainquestion'):
                blockchain_question = obj.question.blockchainquestion
                if blockchain_question.is_blockchain_synced:
                    return format_html('<span style="color: green;">🔗 Synced</span>')
                elif blockchain_question.use_blockchain:
                    return format_html('<span style="color: orange;">⏳ Pending</span>')
            elif isinstance(obj.question, BlockchainQuestion):
                if obj.question.is_blockchain_synced:
                    return format_html('<span style="color: green;">🔗 Synced</span>')
                elif obj.question.use_blockchain:
                    return format_html('<span style="color: orange;">⏳ Pending</span>')
        except AttributeError:
            pass
        return format_html('<span style="color: gray;">💾 Django</span>')
    question_blockchain_status.short_description = 'Blockchain Status'


@admin.register(BlockchainVote)
class BlockchainVoteAdmin(admin.ModelAdmin):
    """Admin for BlockchainVote (readonly)"""
    list_display = [
        'voter_address_short', 
        'question', 
        'choice_text_display', 
        'transaction_hash_short', 
        'timestamp'
    ]
    list_filter = ['timestamp', 'question']
    search_fields = ['voter_address', 'transaction_hash', 'question__question_text']
    readonly_fields = [
        'question', 'choice_index', 'voter_address', 
        'transaction_hash', 'block_number', 'timestamp'
    ]
    
    def has_add_permission(self, request):
        """Disable adding votes through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing votes"""
        return False
    
    def voter_address_short(self, obj):
        """Display shortened voter address"""
        return f"{obj.voter_address[:6]}...{obj.voter_address[-4:]}"
    voter_address_short.short_description = 'Voter'
    
    def transaction_hash_short(self, obj):
        """Display shortened transaction hash"""
        return format_html(
            '<code>{}</code>',
            f"{obj.transaction_hash[:10]}...{obj.transaction_hash[-6:]}"
        )
    transaction_hash_short.short_description = 'Transaction'
    
    def choice_text_display(self, obj):
        """Display the choice text for this vote"""
        return obj.choice_text
    choice_text_display.short_description = 'Choice'


# Register the blockchain models in the main admin
# This ensures they appear in the Django admin interface