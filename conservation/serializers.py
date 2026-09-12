from rest_framework import serializers

from .models import (
    ConservationAlert,
    DamageReport,
    GrowthRecord,
    Guardian,
    GuardianAssignment,
    Tree,
)


class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = "__all__"


class GrowthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrowthRecord
        fields = "__all__"


class DamageReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DamageReport
        fields = "__all__"


class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = "__all__"


class GuardianAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianAssignment
        fields = "__all__"


class ConservationAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConservationAlert
        fields = "__all__"
