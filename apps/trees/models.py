"""
apps/trees/models.py

The Tree model — the heart of TreeGuardian.

Every field is documented so you understand:
  - WHY we chose that field type
  - WHAT the field stores
  - HOW Django uses it

KEY CONCEPTS IN THIS FILE
──────────────────────────
  CharField      → short text (has max_length)
  TextField      → long text (no max_length)
  DecimalField   → precise decimal numbers (max_digits, decimal_places)
  IntegerField   → whole numbers
  DateField      → a calendar date (YYYY-MM-DD)
  DateTimeField  → date + time
  BooleanField   → True / False
  ForeignKey     → link to another model (many-to-one relationship)
  choices        → restrict a field to a fixed list of values
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────────────────────────────────────
# Health Status Choices
# ─────────────────────────────────────────────────────────────────────────────

class HealthStatus(models.TextChoices):
    """
    TextChoices creates an enumeration of allowed string values.
    Django stores the left side ('HEALTHY') in the DB.
    The right side ('🟢 Healthy') is the human-readable label.

    Using choices means:
      - Django validates that only these values are saved
      - The admin shows a dropdown instead of a text box
      - Your serializer exposes the labels in responses
    """
    HEALTHY         = "HEALTHY",         "🟢 Healthy"
    NEEDS_ATTENTION = "NEEDS_ATTENTION", "🟡 Needs Attention"
    AT_RISK         = "AT_RISK",         "🔴 At Risk"
    EMERGENCY       = "EMERGENCY",       "🚨 Emergency"
    LOST            = "LOST",            "💀 Lost / Removed"
    UNKNOWN         = "UNKNOWN",         "❓ Unknown"


class NativeStatus(models.TextChoices):
    NATIVE       = "NATIVE",       "Native"
    INTRODUCED   = "INTRODUCED",   "Introduced"
    NATURALISED  = "NATURALISED",  "Naturalised"
    UNKNOWN      = "UNKNOWN",      "Unknown"


class SunlightRequirement(models.TextChoices):
    FULL_SUN     = "FULL_SUN",     "Full Sun"
    PARTIAL_SUN  = "PARTIAL_SUN",  "Partial Sun / Shade"
    FULL_SHADE   = "FULL_SHADE",   "Full Shade"


class WaterRequirement(models.TextChoices):
    LOW    = "LOW",    "Low — drought-tolerant"
    MEDIUM = "MEDIUM", "Medium — regular watering"
    HIGH   = "HIGH",   "High — frequent watering"


# ─────────────────────────────────────────────────────────────────────────────
# Tree Model
# ─────────────────────────────────────────────────────────────────────────────

class Tree(models.Model):
    """
    A registered tree in the TreeGuardian system.

    One tree has:
      - An identity (tree_id, names, location)
      - Physical data (height, trunk, age)
      - Species info (native status, climate, soil, benefits)
      - Health tracking (status, last verified)
      - A relationship to the user who registered it
    """

    # ─────────────────────────────────────────
    # IDENTITY
    # ─────────────────────────────────────────

    tree_id = models.CharField(
        max_length=20,
        unique=True,  # no two trees can have the same ID
        help_text="Auto-generated unique ID. Format: TG-XXXXXXX",
    )

    common_name = models.CharField(
        max_length=200,
        help_text="Common/local name of the tree, e.g. 'Neem', 'Banyan'.",
    )

    scientific_name = models.CharField(
        max_length=300,
        blank=True,
        default="",
        help_text="Scientific (Latin) name, e.g. 'Azadirachta indica'.",
    )

    # ─────────────────────────────────────────
    # LOCATION
    # ─────────────────────────────────────────

    location_name = models.CharField(
        max_length=300,
        help_text="Human-readable location, e.g. 'Ahmedabad, Gujarat'.",
    )

    # Stored as Decimal for precision.
    # max_digits=9, decimal_places=6 can represent any point on Earth.
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="GPS latitude of the tree.",
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="GPS longitude of the tree.",
    )

    # ─────────────────────────────────────────
    # PHYSICAL DATA
    # ─────────────────────────────────────────

    estimated_age_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated age of the tree in years.",
    )

    planting_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the tree was planted, if known.",
    )

    height_meters = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current measured height in metres.",
    )

    trunk_circumference_cm = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Trunk circumference at chest height, in centimetres.",
    )

    # ─────────────────────────────────────────
    # SPECIES INFO (educational section)
    # ─────────────────────────────────────────

    native_status = models.CharField(
        max_length=20,
        choices=NativeStatus.choices,
        default=NativeStatus.UNKNOWN,
    )

    sunlight_requirement = models.CharField(
        max_length=20,
        choices=SunlightRequirement.choices,
        default=SunlightRequirement.FULL_SUN,
        blank=True,
    )

    water_requirement = models.CharField(
        max_length=10,
        choices=WaterRequirement.choices,
        default=WaterRequirement.MEDIUM,
        blank=True,
    )

    suitable_climate = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Climate zones this species thrives in.",
    )

    soil_requirement = models.TextField(
        blank=True,
        default="",
        help_text="Soil type and quality this species prefers.",
    )

    expected_growth = models.TextField(
        blank=True,
        default="",
        help_text="Expected growth rate and mature size.",
    )

    environmental_benefits = models.TextField(
        blank=True,
        default="",
        help_text="Carbon sequestration, air quality, shade, etc.",
    )

    wildlife_supported = models.TextField(
        blank=True,
        default="",
        help_text="Birds, insects, or mammals that benefit from this tree.",
    )

    additional_notes = models.TextField(
        blank=True,
        default="",
        help_text="Any extra notes about this specific tree.",
    )

    # ─────────────────────────────────────────
    # HEALTH STATUS
    # ─────────────────────────────────────────

    health_status = models.CharField(
        max_length=20,
        choices=HealthStatus.choices,
        default=HealthStatus.HEALTHY,
        help_text="Current health condition of the tree.",
    )

    last_verified = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When was the tree's health last verified by a guardian?",
    )

    # ─────────────────────────────────────────
    # RELATIONSHIPS
    # ─────────────────────────────────────────

    # ForeignKey creates a many-to-one link:
    # Many trees can be registered by one user.
    # on_delete=SET_NULL means: if the user is deleted, don't delete the tree.
    # The tree remains but registered_by becomes NULL.
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registered_trees",
        help_text="The user who first registered this tree.",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="False if the tree has been removed from the active registry.",
    )

    # ─────────────────────────────────────────
    # TIMESTAMPS (auto-managed by Django)
    # ─────────────────────────────────────────

    # auto_now_add=True  →  set once when the object is created, never updated
    created_at = models.DateTimeField(auto_now_add=True)

    # auto_now=True  →  updated every time .save() is called
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tree"
        verbose_name_plural = "Trees"
        ordering = ["-created_at"]  # newest trees first

    def __str__(self):
        return f"{self.tree_id} — {self.common_name} ({self.location_name})"

    def save(self, *args, **kwargs):
        """
        Override save() to auto-generate the tree_id if not set.

        How tree_id is generated:
          TG-0000001, TG-0000002, TG-0000003, ...

        We use the current max id+1 to get the next number.
        In a production system with high concurrency you'd use a
        database sequence or UUID instead, but for learning this is clear.
        """
        if not self.tree_id:
            # Get the current highest auto-incremented PK
            last = Tree.objects.order_by("id").last()
            next_number = (last.id + 1) if last else 1
            self.tree_id = f"TG-{next_number:07d}"  # zero-padded to 7 digits

        super().save(*args, **kwargs)
