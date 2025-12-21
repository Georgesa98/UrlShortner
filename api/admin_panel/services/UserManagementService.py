from api.url.models import Url
from django.contrib.auth import get_user_model
from django.db.models import Q
from typing import List
from django.core.paginator import Paginator

User = get_user_model()


class UserManagementService:
    """Service for administrative user management operations."""

    @staticmethod
    def get_users_with_pagination(
        roles: list = [User.Role.USER, User.Role.STAFF, User.Role.ADMIN],
        is_active: List[bool] = [True, False],
        order_by: str = "-date_joined",
        limit: int = 10,
        page: int = 1,
    ):
        """Get paginated users with filtering.

        Args:
            roles (list, optional): List of user roles to filter. Defaults to all roles.
            is_active (List[bool], optional): Active status filter. Defaults to both.
            order_by (str, optional): Ordering field. Defaults to "-date_joined".
            limit (int, optional): Users per page. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            dict: Users list and pagination info.
        """
        users = User.objects.filter(role__in=roles, is_active__in=is_active).order_by(
            order_by
        )

        paginator = Paginator(users, limit)
        page_obj = paginator.get_page(page)

        user_data = []
        for user in page_obj.object_list:
            user_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined,
                    "last_login": user.last_login,
                }
            )

        return {
            "users": user_data,
            "pagination": {
                "total": paginator.count,
                "page": page_obj.number,
                "limit": paginator.per_page,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }

    @staticmethod
    def toggle_ban_user(user_id: str):
        """Toggle active status of a user (ban/unban).

        Args:
            user_id (str): The user ID.

        Returns:
            User: The updated user instance.
        """
        user_instance = User.objects.get(id=user_id)
        user_instance.is_active = not user_instance.is_active
        user_instance.save()
        return user_instance

    @staticmethod
    def bulk_user_deletion(user_ids: list):
        """Delete multiple users by their IDs.

        Args:
            user_ids (list): List of user IDs to delete.

        Returns:
            int: Number of users deleted.
        """
        users_to_delete = User.objects.filter(id__in=user_ids)
        count, _ = users_to_delete.delete()
        return count

    @staticmethod
    def get_user_details(user_id: str):
        """Get detailed information about a user including their URLs.

        Args:
            user_id (str): The user ID.

        Returns:
            dict: User details with associated URLs.
        """
        url_instances = Url.objects.select_related("user", "url_status").filter(
            user__id=user_id
        )
        return {"user": url_instances[0].user, "urls": url_instances}

    @staticmethod
    def search_users_with_pagination(query: str, limit: int = 10, page: int = 1):
        """Search users by query with pagination.

        Args:
            query (str): Search query for username, first_name, or last_name.
            limit (int, optional): Results per page. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            dict: Search results with users and pagination info.
        """
        users = User.objects.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )

        paginator = Paginator(users, limit)
        page_obj = paginator.get_page(page)

        user_data = []
        for user in page_obj.object_list:
            user_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "date_joined": user.date_joined,
                    "last_login": user.last_login,
                }
            )

        return {
            "users": user_data,
            "pagination": {
                "total": paginator.count,
                "page": page_obj.number,
                "limit": paginator.per_page,
                "total_pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            },
        }
