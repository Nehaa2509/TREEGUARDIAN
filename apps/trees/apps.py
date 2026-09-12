"""
apps/trees/apps.py
"""

from django.apps import AppConfig


class TreesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.trees"
    verbose_name = "Trees"
