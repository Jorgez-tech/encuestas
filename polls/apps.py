from django.apps import AppConfig


class PollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'polls'
    
    def ready(self):
        """Called when app is ready - import blockchain models"""
        try:
            from .blockchain import models as blockchain_models
        except ImportError:
            pass  # Blockchain models not available
