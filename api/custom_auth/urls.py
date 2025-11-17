from django.urls import path

from api.custom_auth.views import CookieTokenObtainPairView

urlpatterns = [
    path("jwt/create/", CookieTokenObtainPairView.as_view(), name="jwt_create")
]
