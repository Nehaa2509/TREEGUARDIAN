import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ConservationAlert, DamageReport, GrowthRecord, Guardian, GuardianAssignment, Tree


class TreeGuardianApiTests(APITestCase):
    def setUp(self):
        self.tree = Tree.objects.create(
            species="Mangifera indica",
            care_information="Water weekly and mulch annually.",
            lifecycle_stage="young",
            latitude=12.971600,
            longitude=77.594600,
        )

    def test_tree_has_digital_identity(self):
        self.assertIsInstance(self.tree.digital_identity, uuid.UUID)

    def test_growth_records_are_saved_per_tree(self):
        GrowthRecord.objects.create(tree=self.tree, recorded_on="2026-01-05", height_cm=120, notes="Healthy")

        response = self.client.get(reverse("growthrecord-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["tree"], self.tree.id)

    def test_tree_exposes_species_and_care_information(self):
        response = self.client.get(reverse("tree-detail", args=[self.tree.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["species"], "Mangifera indica")
        self.assertIn("Water weekly", response.data["care_information"])

    def test_damage_report_requires_evidence_url(self):
        payload = {
            "tree": self.tree.id,
            "description": "Trunk bark stripped",
            "evidence_url": "https://example.org/evidence.jpg",
            "severity": "high",
        }

        response = self.client.post(reverse("damagereport-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DamageReport.objects.count(), 1)

    def test_guardian_assignments_support_community_guardians(self):
        guardian = Guardian.objects.create(name="Asha", contact="asha@example.org")
        GuardianAssignment.objects.create(tree=self.tree, guardian=guardian)

        response = self.client.get(reverse("guardianassignment-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["guardian"], guardian.id)

    def test_tree_alerts_return_only_location_based_alerts(self):
        ConservationAlert.objects.create(
            title="Pest infestation warning",
            message="Recent bark beetle cases reported nearby.",
            latitude=12.972000,
            longitude=77.595000,
            radius_km=2.0,
            is_active=True,
        )
        ConservationAlert.objects.create(
            title="Storm damage advisory",
            message="Strong winds expected.",
            latitude=28.704100,
            longitude=77.102500,
            radius_km=1.0,
            is_active=True,
        )

        response = self.client.get(reverse("tree-alerts", args=[self.tree.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Pest infestation warning")
