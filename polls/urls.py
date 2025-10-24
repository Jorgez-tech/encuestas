from django.urls import path
from . import views
from .blockchain import views as blockchain_views

app_name = 'polls'
urlpatterns = [
    # Traditional URLs (legacy compatibility)
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('<int:question_id>/results/', views.results, name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),
    
    # Hybrid URLs (Django + Blockchain)
    path('hybrid/', blockchain_views.hybrid_index, name='hybrid_index'),
    path('hybrid/<int:question_id>/', blockchain_views.hybrid_detail, name='hybrid_detail'),
    path('hybrid/<int:question_id>/results/', blockchain_views.hybrid_results, name='hybrid_results'),
    path('hybrid/<int:question_id>/vote/', blockchain_views.hybrid_vote, name='hybrid_vote'),
    
    # Blockchain-specific URLs
    path('blockchain/status/', blockchain_views.blockchain_status, name='blockchain_status'),
    path('blockchain/create/', blockchain_views.create_blockchain_question, name='create_blockchain_question'),
    path('blockchain/sync/<int:question_id>/', blockchain_views.sync_question_to_blockchain, name='sync_to_blockchain'),
]
