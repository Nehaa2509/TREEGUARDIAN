import math
import uuid

from django.db import models


class Tree(models.Model):
    digital_identity = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    species = models.CharField(max_length=120)
    care_information = models.TextField()
    lifecycle_stage = models.CharField(max_length=60)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


class GrowthRecord(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="growth_records")
    recorded_on = models.DateField()
    height_cm = models.PositiveIntegerField()
    notes = models.TextField(blank=True)


class DamageReport(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="damage_reports")
    description = models.TextField()
    evidence_url = models.URLField()
    severity = models.CharField(max_length=30)
    reported_at = models.DateTimeField(auto_now_add=True)


class Guardian(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField(unique=True)


class GuardianAssignment(models.Model):
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE, related_name="guardian_assignments")
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE, related_name="tree_assignments")
    assigned_on = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("tree", "guardian")


class ConservationAlert(models.Model):
    title = models.CharField(max_length=120)
    message = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    radius_km = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)

    def applies_to_tree(self, tree: Tree) -> bool:
        earth_radius_km = 6371

        lat1 = math.radians(float(self.latitude))
        lon1 = math.radians(float(self.longitude))
        lat2 = math.radians(float(tree.latitude))
        lon2 = math.radians(float(tree.longitude))

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1

        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distance = earth_radius_km * c

        return distance <= self.radius_km
