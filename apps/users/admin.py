"""
apps/users/admin.py

Registers the User model with Django Admin.
After this, you can visit /admin/ to see, create, edit,
and delete users through a nice web interface — without writing any code.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Extends Django's built-in UserAdmin to show our custom fields
    alongside the default username/email/password management.
    """

    # Columns shown in the user list
    list_display = [
        "username",
        "email",
        "full_name",
        "location",
        "guardian_since",
        "is_staff",
        "date_joined",
    ]

    list_filter = ["is_staff", "is_active", "guardian_since", "receive_emergency_alerts"]

    search_fields = ["username", "email", "first_name", "last_name", "location"]

    # Add our custom fields to the existing fieldsets
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "TreeGuardian Profile",
            {
                "fields": (
                    "bio",
                    "location",
                    "profile_photo",
                    "guardian_since",
                    "guardian_area",
                    "guardian_radius_km",
                    "receive_emergency_alerts",
                    "receive_care_reminders",
                )
            },
        ),
    )
