"""
apps/users/serializers.py

WHAT IS A SERIALIZER?
─────────────────────
A serializer does two jobs:
  1. Serialization   → Python object  →  JSON  (when sending a response)
  2. Deserialization → JSON  →  Python object  (when receiving a request)

ModelSerializer is a shortcut: it reads your model's fields and builds
the serializer almost automatically. You only need to describe exceptions.

HOW TO READ THESE:
  class Meta:
      model  = which model this serializer is for
      fields = which fields to include

  read_only_fields = fields the client can SEE but cannot SET
                     (e.g. id, created_at — the server sets these)
"""

from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


# ─────────────────────────────────────────────────────────────────────────────
# 1. UserSerializer  — for viewing a user profile (GET requests)
# ─────────────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """
    Serializes a full User profile.
    Used for the /api/auth/profile/ endpoint.
    """

    full_name = serializers.ReadOnlyField()
    # ReadOnlyField reads a model property (@property) but never writes to it.

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "bio",
            "location",
            "profile_photo",
            "guardian_since",
            "guardian_area",
            "guardian_radius_km",
            "receive_emergency_alerts",
            "receive_care_reminders",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. RegisterSerializer — for creating a new user (POST /api/auth/register/)
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration.

    We add a `password_confirm` field that is NOT on the model —
    it only exists here to let the client confirm the password.

    `write_only=True` means the field is accepted in requests
    but never sent back in responses. Passwords should NEVER appear in API output.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},  # shows as *** in the browsable API
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
            "location",
        ]

    def validate(self, data):
        """
        `validate()` runs after individual field validation.
        Here we check that the two passwords match.
        If they don't, we raise a ValidationError — DRF sends a 400 response.
        """
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        """
        `create()` is called by `serializer.save()` in the view.

        We must:
          1. Remove password_confirm (not a model field)
          2. Use `create_user()` — NOT `User.objects.create()` —
             because create_user() hashes the password correctly.
             If you used create() directly, the password would be stored
             as plain text and logins would break.
        """
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)  # hashes the password
        user.save()
        return user


# ─────────────────────────────────────────────────────────────────────────────
# 3. LoginSerializer — for authenticating a user (POST /api/auth/login/)
# ─────────────────────────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    """
    Note: this is plain `Serializer`, not `ModelSerializer`.
    We use it only for validation — the fields don't map to a model.

    `authenticate()` is Django's built-in function that checks
    username + password against the database.
    """

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )
        if not user:
            raise serializers.ValidationError(
                "Invalid username or password. Please try again."
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "This account has been deactivated."
            )

        # Attach the user object so the view can access it via
        # serializer.validated_data['user']
        data["user"] = user
        return data
