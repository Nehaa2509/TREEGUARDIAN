"""
apps/trees/serializers.py

TWO SERIALIZERS: WHY?
─────────────────────
We have two serializers for Tree because different endpoints need
different amounts of data:

  TreeListSerializer   →  compact, for list/map views (only essential fields)
                           Used by: GET /api/trees/

  TreeDetailSerializer →  complete, for the full profile page
                           Used by: GET /api/trees/{id}/

This is a very common DRF pattern. Sending 30 fields for every item
in a list of 1000 trees would be very slow. Keep list views lean.

SERIALIZER METHOD FIELDS
─────────────────────────
`SerializerMethodField` lets you add a computed field that doesn't exist
on the model. You write a `get_<field_name>()` method, and DRF calls it.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tree, HealthStatus

User = get_user_model()


# ─────────────────────────────────────────────────────────────────────────────
# Helper: tiny user representation (used inside tree serializers)
# ─────────────────────────────────────────────────────────────────────────────

class TreeRegisteredBySerializer(serializers.ModelSerializer):
    """A minimal user card: just enough to display who registered the tree."""

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


# ─────────────────────────────────────────────────────────────────────────────
# 1. TreeListSerializer — lean, for list/map views
# ─────────────────────────────────────────────────────────────────────────────

class TreeListSerializer(serializers.ModelSerializer):
    """
    Returns only the fields needed to show a tree on a map or in a list.
    Less data = faster API responses.
    """

    health_status_display = serializers.CharField(
        source="get_health_status_display",  # Django auto-generates this for choices fields
        read_only=True,
    )

    class Meta:
        model = Tree
        fields = [
            "id",
            "tree_id",
            "common_name",
            "scientific_name",
            "location_name",
            "latitude",
            "longitude",
            "health_status",
            "health_status_display",
            "estimated_age_years",
            "created_at",
        ]
        read_only_fields = ["id", "tree_id", "created_at"]


# ─────────────────────────────────────────────────────────────────────────────
# 2. TreeDetailSerializer — full profile, for the tree detail page
# ─────────────────────────────────────────────────────────────────────────────

class TreeDetailSerializer(serializers.ModelSerializer):
    """
    Returns every field — used when the user opens a tree's full profile.

    Notice how we nest `registered_by` as a serializer:
    Instead of returning just the user's ID (e.g. 3), we return
    a full object:
        "registered_by": {
            "id": 3,
            "username": "sneha",
            ...
        }
    This is called a nested serializer.
    """

    registered_by = TreeRegisteredBySerializer(read_only=True)
    # read_only=True because the API doesn't let clients change who registered a tree

    # The human-readable label for the choices field
    health_status_display = serializers.CharField(
        source="get_health_status_display",
        read_only=True,
    )
    native_status_display = serializers.CharField(
        source="get_native_status_display",
        read_only=True,
    )
    sunlight_display = serializers.CharField(
        source="get_sunlight_requirement_display",
        read_only=True,
    )
    water_display = serializers.CharField(
        source="get_water_requirement_display",
        read_only=True,
    )

    # A computed field showing the tree's age clearly
    age_description = serializers.SerializerMethodField()

    class Meta:
        model = Tree
        fields = [
            # Identity
            "id",
            "tree_id",
            "common_name",
            "scientific_name",

            # Location
            "location_name",
            "latitude",
            "longitude",

            # Physical
            "estimated_age_years",
            "age_description",
            "planting_date",
            "height_meters",
            "trunk_circumference_cm",

            # Species info
            "native_status",
            "native_status_display",
            "sunlight_requirement",
            "sunlight_display",
            "water_requirement",
            "water_display",
            "suitable_climate",
            "soil_requirement",
            "expected_growth",
            "environmental_benefits",
            "wildlife_supported",
            "additional_notes",

            # Health
            "health_status",
            "health_status_display",
            "last_verified",

            # Relations
            "registered_by",
            "is_active",

            # Timestamps
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "tree_id", "registered_by", "created_at", "updated_at"]

    def get_age_description(self, obj):
        """
        SerializerMethodField: returns a friendly string about the tree's age.
        `obj` is the Tree instance being serialized.
        """
        if obj.planting_date:
            from django.utils import timezone
            years = (timezone.now().date() - obj.planting_date).days // 365
            return f"Planted {obj.planting_date.year} — approximately {years} years old"
        if obj.estimated_age_years:
            return f"Approximately {obj.estimated_age_years} years old"
        return "Age unknown"

    def validate_health_status(self, value):
        """
        Field-level validation.
        DRF calls `validate_<fieldname>()` automatically.
        """
        valid = [choice[0] for choice in HealthStatus.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"Invalid health status. Choose from: {valid}"
            )
        return value

    def create(self, validated_data):
        """
        When creating a tree, automatically set `registered_by`
        to the currently logged-in user.

        self.context['request'] — DRF passes the request object
        into the serializer context from the view. This is how
        a serializer can access the logged-in user.
        """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["registered_by"] = request.user
        return super().create(validated_data)
