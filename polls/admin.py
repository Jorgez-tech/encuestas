from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Question, Choice

# Import blockchain admin components
try:
    from .blockchain import admin as blockchain_admin
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently', 'blockchain_link')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    
    def blockchain_link(self, obj):
        """Show link to blockchain features if available"""
        if BLOCKCHAIN_AVAILABLE:
            return format_html(
                '<a href="/admin/polls/blockchainquestion/" style="color: #0c7cd5;">🔗 Blockchain Version</a>'
            )
        return format_html('<span style="color: #ccc;">Blockchain N/A</span>')
    blockchain_link.short_description = 'Blockchain'
    blockchain_link.allow_tags = True


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'votes')
    list_filter = ['question']
    search_fields = ['choice_text']


# Custom admin site modifications
class PollsAdminSite(admin.AdminSite):
    """Custom admin site with blockchain dashboard"""
    site_header = 'Polls Administration (with Blockchain)'
    site_title = 'Polls Admin'
    index_title = 'Welcome to Polls Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = []
        
        if BLOCKCHAIN_AVAILABLE:
            custom_urls = [
                path(
                    'blockchain-dashboard/',
                    self.admin_view(self.blockchain_dashboard_redirect),
                    name='blockchain_dashboard',
                ),
            ]
        
        return custom_urls + urls
    
    def blockchain_dashboard_redirect(self, request):
        """Redirect to the blockchain dashboard"""
        return redirect('/admin/polls/blockchainquestion/blockchain-dashboard/')
    
    def index(self, request, extra_context=None):
        """Custom index with blockchain info"""
        extra_context = extra_context or {}
        
        if BLOCKCHAIN_AVAILABLE:
            from .blockchain.config import is_web3_connected
            extra_context['blockchain_available'] = True
            extra_context['blockchain_connected'] = is_web3_connected()
        else:
            extra_context['blockchain_available'] = False
            extra_context['blockchain_connected'] = False
        
        return super().index(request, extra_context)


# Override the default admin site if blockchain is available
if BLOCKCHAIN_AVAILABLE:
    # Create custom admin site instance
    custom_admin_site = PollsAdminSite(name='polls_admin')
    
    # Register models with custom site
    custom_admin_site.register(Question, QuestionAdmin)
    custom_admin_site.register(Choice, ChoiceAdmin)
    
    # Register blockchain models
    from .blockchain.models import BlockchainQuestion, BlockchainChoice, BlockchainVote
    custom_admin_site.register(BlockchainQuestion, blockchain_admin.BlockchainQuestionAdmin)
    custom_admin_site.register(BlockchainChoice, blockchain_admin.BlockchainChoiceAdmin)
    custom_admin_site.register(BlockchainVote, blockchain_admin.BlockchainVoteAdmin)
