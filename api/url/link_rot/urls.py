from django.urls import path
from . import views

urlpatterns = [
    path(
        "check-url-health/<int:url_id>/",
        views.CheckUrlHealthView.as_view(),
        name="check-url-health",
    ),
    path(
        "check-batch-health/",
        views.CheckBatchHealthView.as_view(),
        name="check-batch-health",
    ),
]
