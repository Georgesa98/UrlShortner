from django.urls import path
from . import views

urlpatterns = [
    path("logs/", views.GetAuditLogsView.as_view(), name="audit-logs"),
]
