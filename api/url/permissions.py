from rest_framework import permissions
from api.url.models import Url


class IsUrlOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Url):
            return obj.user == request.user

        return False
