from django.urls import path, include

urlpatterns = [
    path("system/", include("api.admin_panel.system.urls")),
    path("url/", include("api.admin_panel.url_management.urls")),
    path("user/", include("api.admin_panel.user_management.urls")),
    path("insight/", include("api.admin_panel.insight.urls")),
    path("audit/", include("api.admin_panel.audit.urls")),
    path("fraud/", include("api.admin_panel.fraud.urls")),
]
