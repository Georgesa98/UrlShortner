from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
from api.custom_auth.models import CustomUser

User = get_user_model()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.id)
        return user.role == CustomUser.Role.ADMIN


class IsAdminOrStaff(BasePermission):
    def has_permission(self, request, view):
        user = User.objects.get(pk=request.user.id)
        return user.role == CustomUser.Role.STAFF or user.role == CustomUser.Role.ADMIN
