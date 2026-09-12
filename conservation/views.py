from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    ConservationAlert,
    DamageReport,
    GrowthRecord,
    Guardian,
    GuardianAssignment,
    Tree,
)
from .serializers import (
    ConservationAlertSerializer,
    DamageReportSerializer,
    GrowthRecordSerializer,
    GuardianAssignmentSerializer,
    GuardianSerializer,
    TreeSerializer,
)


class TreeViewSet(viewsets.ModelViewSet):
    queryset = Tree.objects.all()
    serializer_class = TreeSerializer

    @action(detail=True, methods=["get"])
    def alerts(self, request, pk=None):
        tree = self.get_object()
        queryset = [alert for alert in ConservationAlert.objects.filter(is_active=True) if alert.applies_to_tree(tree)]
        serializer = ConservationAlertSerializer(queryset, many=True)
        return Response(serializer.data)


class GrowthRecordViewSet(viewsets.ModelViewSet):
    queryset = GrowthRecord.objects.all()
    serializer_class = GrowthRecordSerializer


class DamageReportViewSet(viewsets.ModelViewSet):
    queryset = DamageReport.objects.all()
    serializer_class = DamageReportSerializer


class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.all()
    serializer_class = GuardianSerializer


class GuardianAssignmentViewSet(viewsets.ModelViewSet):
    queryset = GuardianAssignment.objects.all()
    serializer_class = GuardianAssignmentSerializer


class ConservationAlertViewSet(viewsets.ModelViewSet):
    queryset = ConservationAlert.objects.all()
    serializer_class = ConservationAlertSerializer
