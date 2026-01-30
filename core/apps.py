"""
Core application configuration for Clean Architecture implementation.

This app contains the domain layer (entities and interfaces) and 
application layer (use cases) that are independent of Django and 
external frameworks.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the Core app (Clean Architecture layers)"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Core Domain & Use Cases'
