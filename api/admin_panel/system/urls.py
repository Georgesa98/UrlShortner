from django.urls import path
from api.admin_panel.system.views import (
    HealthView,
    ListSystemConfigurationView,
    SpecificSystemConfigurationView,
    BatchCreateSystemConfigurationView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="system-health"),
    path("config/", ListSystemConfigurationView.as_view(), name="system-config-list"),
    path(
        "config/batch/",
        BatchCreateSystemConfigurationView.as_view(),
        name="system-config-batch",
    ),
    path(
        "config/<str:key>/",
        SpecificSystemConfigurationView.as_view(),
        name="system-config-detail",
    ),
]
