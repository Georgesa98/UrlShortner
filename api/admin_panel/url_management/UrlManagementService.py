from api.analytics.models import Visit
from api.url.models import Url, UrlStatus
from django.contrib.auth import get_user_model
from typing import Dict, List, Any
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator

User = get_user_model()


class UrlManagementService:
    """Service for administrative URL management operations."""

    @staticmethod
    def urls_stats() -> dict:
        """
        Get statistics for all URLs.

        Returns:
            dict: Statistics for all URLs.
        """
        total_urls = Url.objects.count()
        active_urls = Url.objects.filter(
            url_status__state=UrlStatus.State.ACTIVE
        ).count()
        inactive_urls = Url.objects.filter(
            Q(url_status__state=UrlStatus.State.EXPIRED)
            | Q(url_status__state=UrlStatus.State.DISABLED)
            | Q(url_status__state=UrlStatus.State.BROKEN)
        ).count()
        flagged_urls = Url.objects.filter(
            url_status__state=UrlStatus.State.FLAGGED
        ).count()
        return {
            "total_urls": total_urls,
            "active_urls": active_urls,
            "flagged_urls": flagged_urls,
            "inactive_urls": inactive_urls,
        }

    @staticmethod
    def list_urls(
        limit: int = 10,
        page: int = 1,
        url_status: str = None,
        date_order: str = None,
        query: str = None,
    ) -> dict:
        """List URLs with pagination.

        Args:
            limit (int, optional): Number of URLs per page. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.
            url_status (str, optional): URL status to filter by. Defaults to None.
            date_order (str, optional): Date order to sort by. Defaults to None.

        Returns:
            dict: URLs list and pagination info.
        """
        queryset = Url.objects.select_related("url_status", "user").all()
        if url_status:
            queryset = queryset.filter(url_status__state=url_status)
        if date_order:
            queryset = queryset.order_by(date_order)
        if query:
            queryset = queryset.filter(
                Q(long_url__icontains=query)
                | Q(short_url__icontains=query)
                | Q(name__icontains=query)
            )
        paginator = Paginator(queryset, limit)
        page_obj = paginator.get_page(page)
        return {
            "urls": page_obj.object_list,
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
    def get_user_urls_with_pagination(
        user_id: int, limit: int = 10, page: int = 1
    ) -> dict:
        """Get paginated URLs for a specific user.

        Args:
            user_id (int): The user ID.
            limit (int, optional): Number of URLs per page. Defaults to 10.
            page (int, optional): Page number. Defaults to 1.

        Returns:
            dict: Contains 'urls' (QuerySet) and 'pagination' details.
        """
        urls = Url.objects.select_related("url_status", "user").filter(user__id=user_id)

        paginator = Paginator(urls, limit)
        page_obj = paginator.get_page(page)

        return {
            "urls": page_obj.object_list,
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
    def bulk_url_deletion(url_ids: list) -> int:
        """Delete multiple URLs by their IDs.

        Args:
            url_ids (list): List of URL IDs to delete.

        Returns:
            int: Number of URLs deleted.
        """
        urls_to_delete = Url.objects.filter(id__in=url_ids)
        count, _ = urls_to_delete.delete()
        return count

    @staticmethod
    def bulk_flag_url(data: List[Dict[str, Any]]) -> dict:
        """Bulk update URL statuses with flagging.

        Args:
            data (List[Dict[str, Any]]): List of dicts with url_id, state, and optional reason.

        Returns:
            dict: Results with success_count and failed_items.
        """
        with transaction.atomic():
            success_count = 0
            failed_items = []

            for item in data:
                try:
                    url = Url.objects.select_related("url_status").get(
                        id=item["url_id"]
                    )
                    url.url_status.state = item["state"]
                    url.url_status.reason = item.get("reason", "")
                    url.url_status.save()
                    success_count += 1

                except Url.DoesNotExist:
                    failed_items.append(
                        {"url_id": item["url_id"], "error": "URL not found"}
                    )
                except Exception as e:
                    failed_items.append({"url_id": item["url_id"], "error": str(e)})
            return {"success_count": success_count, "failed_items": failed_items}

    @staticmethod
    def get_url_details(url_id: str) -> dict:
        """Get detailed information about a specific URL.

        Args:
            url_id (str): The URL ID.

        Returns:
            dict: URL details including status and recent clicks.
        """
        url_instance = Url.objects.select_related("url_status").get(id=url_id)
        recent_clicks = Visit.objects.filter(url=url_instance).order_by("-timestamp")[
            :10
        ]
        return {
            "url": url_instance,
            "url_status": url_instance.url_status,
            "recent_clicks": recent_clicks,
        }

    @staticmethod
    def updated_url_destination(short_url: str, new_destination: str) -> object:
        """Update the destination URL for a short URL.

        Args:
            short_url (str): The short URL identifier.
            new_destination (str): The new long URL destination.

        Returns:
            Url: The updated URL instance.
        """
        url_instance = Url.objects.get(short_url=short_url)
        url_instance.long_url = new_destination
        url_instance.save()
        return url_instance
