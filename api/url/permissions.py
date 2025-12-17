from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission
from api.url.models import Url

User = get_user_model()


class IsUrlOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Url):
            return obj.user == request.user or request.user.role == User.Role.ADMIN

        return False
