from django.urls import path
from api.admin_panel.fraud.views import FraudOverviewView

urlpatterns = [
    path("overview/", FraudOverviewView.as_view(), name="fraud-overview"),
]
