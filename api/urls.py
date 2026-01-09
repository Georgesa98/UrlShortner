from django.urls import path, re_path, include

urlpatterns = [
    path("admin/", include("api.admin_panel.urls")),
    path("auth/", include("api.custom_auth.urls")),
    path("url/", include("api.url.urls")),
    path("analytics/", include("api.analytics.urls")),
    path("link-rot/", include("api.url.link_rot.urls")),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
]
