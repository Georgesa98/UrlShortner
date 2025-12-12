from django.urls import path
from api.admin_panel.system.views import HealthView

urlpatterns = [path("health/", HealthView.as_view())]
