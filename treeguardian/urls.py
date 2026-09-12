from django.urls import include, path
from rest_framework.routers import DefaultRouter

from conservation.views import (
    ConservationAlertViewSet,
    DamageReportViewSet,
    GrowthRecordViewSet,
    GuardianAssignmentViewSet,
    GuardianViewSet,
    TreeViewSet,
)

router = DefaultRouter()
router.register("trees", TreeViewSet)
router.register("growth-records", GrowthRecordViewSet)
router.register("damage-reports", DamageReportViewSet)
router.register("guardians", GuardianViewSet)
router.register("guardian-assignments", GuardianAssignmentViewSet)
router.register("alerts", ConservationAlertViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
