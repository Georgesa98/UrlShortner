from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from django.utils import timezone

# Create your views here.


class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data["access"]
            refresh_token = response.data["refresh"]
            del response.data["access"]
            del response.data["refresh"]
            now = timezone.now()
            access_expires = now + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
            refresh_expires = now + settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
            response.set_cookie(
                "access_token",
                access_token,
                httponly=True,
                secure=False,  # Change to True in production
                samesite="Lax",
                expires=access_expires,
            )

            response.set_cookie(
                "refresh_token",
                refresh_token,
                httponly=True,
                secure=False,  # Change to True in production
                samesite="Lax",
                expires=refresh_expires,
            )
            response.data["message"] = "Login successful"
            return response
