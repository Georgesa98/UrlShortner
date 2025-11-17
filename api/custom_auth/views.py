from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime, timedelta, timezone
from config import settings

# Create your views here.


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]

            del response.data["access"]
            del response.data["refresh"]

            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=False,  # Change to True in production
                samesite="Lax",
                expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=False,  # Change to True in production
                samesite="Lax",
                expires=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
            )
            response.data["message"] = "Login successful"
            return response
