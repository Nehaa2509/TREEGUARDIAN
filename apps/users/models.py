"""
apps/users/models.py

Custom User model for TreeGuardian.

WHY extend AbstractUser?
────────────────────────
Django's built-in User model has username, email, first_name, last_name,
password, is_staff, is_active, etc. already.

AbstractUser gives us all of that, and lets us ADD our own fields.
This is always recommended over using the default User model, because
once you start a project and make migrations, changing the user model
later is very painful.

So we do it right from the start.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    TreeGuardian user.

    Inherits from AbstractUser, which already provides:
        username, email, first_name, last_name, password,
        is_staff, is_active, is_superuser, date_joined, last_login

    We add TreeGuardian-specific fields below.
    """

    # ──────────────────────────────────────────
    # Personal info
    # ──────────────────────────────────────────
    bio = models.TextField(
        blank=True,
        default="",
        help_text="Short personal bio or motivation for joining TreeGuardian.",
    )

    location = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="City or region where the user is based.",
    )

    profile_photo = models.ImageField(
        upload_to="users/photos/",
        null=True,
        blank=True,
        help_text="Profile picture of the user.",
    )

    # ──────────────────────────────────────────
    # TreeGuardian role
    # ──────────────────────────────────────────
    guardian_since = models.DateField(
        null=True,
        blank=True,
        help_text="Date the user became a registered Tree Guardian.",
    )

    guardian_area = models.CharField(
        max_length=300,
        blank=True,
        default="",
        help_text="Area/city the user has opted to receive tree alerts for.",
    )

    guardian_radius_km = models.PositiveIntegerField(
        default=5,
        help_text="Radius (km) around which the user wants to receive alerts.",
    )

    # ──────────────────────────────────────────
    # Notification preferences
    # ──────────────────────────────────────────
    receive_emergency_alerts = models.BooleanField(
        default=False,
        help_text="User has opted in to receive emergency tree-threat alerts.",
    )

    receive_care_reminders = models.BooleanField(
        default=True,
        help_text="User wants reminders for care tasks on their adopted trees.",
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def full_name(self):
        """Convenience: returns 'First Last' or username if name not set."""
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username
