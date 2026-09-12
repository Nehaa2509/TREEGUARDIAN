"""
apps/trees/admin.py

Registers Tree with Django Admin so you can browse,
create, edit, and search trees at /admin/.
"""

from django.contrib import admin
from .models import Tree


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    """
    Customise how trees appear in the Django Admin.
    """

    # Columns shown in the tree list
    list_display = [
        "tree_id",
        "common_name",
        "scientific_name",
        "location_name",
        "health_status",
        "estimated_age_years",
        "registered_by",
        "created_at",
    ]

    list_filter = [
        "health_status",
        "native_status",
        "water_requirement",
        "sunlight_requirement",
        "is_active",
    ]

    search_fields = [
        "tree_id",
        "common_name",
        "scientific_name",
        "location_name",
    ]

    readonly_fields = ["tree_id", "created_at", "updated_at"]

    fieldsets = (
        (
            "Identity",
            {
                "fields": ("tree_id", "common_name", "scientific_name"),
            },
        ),
        (
            "Location",
            {
                "fields": ("location_name", "latitude", "longitude"),
            },
        ),
        (
            "Physical Data",
            {
                "fields": (
                    "estimated_age_years",
                    "planting_date",
                    "height_meters",
                    "trunk_circumference_cm",
                ),
            },
        ),
        (
            "Species Information",
            {
                "fields": (
                    "native_status",
                    "sunlight_requirement",
                    "water_requirement",
                    "suitable_climate",
                    "soil_requirement",
                    "expected_growth",
                    "environmental_benefits",
                    "wildlife_supported",
                ),
                "classes": ("collapse",),  # collapsible section
            },
        ),
        (
            "Health & Status",
            {
                "fields": ("health_status", "last_verified", "is_active"),
            },
        ),
        (
            "Registry",
            {
                "fields": ("registered_by", "additional_notes", "created_at", "updated_at"),
            },
        ),
    )
