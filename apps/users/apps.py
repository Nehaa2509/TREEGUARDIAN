"""
apps/users/apps.py

AppConfig tells Django the human-readable name of the app
and where its models live. Django uses this during migrations.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
    verbose_name = "Users"
