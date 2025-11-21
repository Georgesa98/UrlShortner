from django.urls import path, re_path, include

urlpatterns = [
    path("auth/", include("api.custom_auth.urls")),
    path("url/", include("api.url.urls")),
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
]
