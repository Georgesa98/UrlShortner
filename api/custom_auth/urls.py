from django.urls import path

from api.custom_auth.views import CookieTokenObtainPairView, LogoutView

urlpatterns = [
    path("jwt/create/", CookieTokenObtainPairView.as_view(), name="jwt_create"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
