from django.urls import path, include

urlpatterns = [
    path("system/", include("api.admin_panel.system.urls")),
    path("insight/", include("api.admin_panel.insight.urls")),
]
