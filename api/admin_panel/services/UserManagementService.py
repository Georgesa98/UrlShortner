from api.url.models import Url
from django.contrib.auth import get_user_model
from django.db.models import Q
from typing import List

User = get_user_model()


class UserManagementService:
    @staticmethod
    def get_users(
        roles: list = [User.Role.USER, User.Role.STAFF, User.Role.ADMIN],
        is_active: List[bool] = [True, False],
        order_by: str = "-date_joined",
    ):
        return User.objects.filter(role=roles, is_active=is_active).order_by(order_by)

    @staticmethod
    def toggle_ban_user(user_id: str):
        user_instance = User.objects.get(id=user_id)
        user_instance.is_active = not user_instance.is_active
        user_instance.save()
        return user_instance

    @staticmethod
    def bulk_user_deletion(user_ids: list):
        users_to_delete = User.objects.filter(id__in=user_ids)
        count, _ = users_to_delete.delete()
        return count

    @staticmethod
    def get_user_details(user_id: str):
        user_instance = User.objects.get(id=user_id)
        url_instances = Url.objects.filter(user=user_instance)
        return {"user": user_instance, "urls": url_instances}

    @staticmethod
    def search_users(query: str):
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
        return users
