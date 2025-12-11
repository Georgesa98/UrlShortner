from django.urls import path, re_path, include
from api.admin_panel.views import HealthView

urlpatterns = [
    path("auth/", include("api.custom_auth.urls")),
    path("url/", include("api.url.urls")),
    path("system/health/", HealthView.as_view()),
    path("analytics/", include("api.analytics.urls")),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
]
