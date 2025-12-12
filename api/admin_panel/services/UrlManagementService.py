from api.analytics.models import Visit
from api.url.models import Url, UrlStatus
from django.contrib.auth import get_user_model
from typing import Dict, List, Any
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator

User = get_user_model()


class UrlManagementService:
    @staticmethod
    def get_user_urls_with_pagination(user_id: int, limit: int = 10, page: int = 1):
        owner = User.objects.get(pk=user_id)
        urls = Url.objects.prefetch_related("url_status").filter(user=owner)

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
    def bulk_url_deletion(url_ids: list):
        urls_to_delete = Url.objects.filter(id__in=url_ids)
        count, _ = urls_to_delete.delete()
        return count

    @staticmethod
    def bulk_flag_url(data: List[Dict[str, Any]]):
        with transaction.atomic():
            success_count = 0
            failed_items = []

            for item in data:
                try:
                    url = Url.objects.get(id=item["url_id"])
                    url_status = UrlStatus.objects.get(url=url)
                    url_status.state = item["state"]
                    url_status.reason = item.get("reason", "")
                    url_status.save()
                    success_count += 1

                except Url.DoesNotExist:
                    failed_items.append(
                        {"url_id": item["url_id"], "error": "URL not found"}
                    )
                except Exception as e:
                    failed_items.append({"url_id": item["url_id"], "error": str(e)})
            return {"success_count": success_count, "failed_items": failed_items}

    @staticmethod
    def get_url_details(url_id: str):
        url_instance = Url.objects.get(id=url_id)
        url_status_instance = UrlStatus.objects.get(url=url_instance)
        recent_clicks = Visit.objects.filter(url=url_instance).order_by("-timestamp")[
            :10
        ]
        return {
            "url": url_instance,
            "url_status": url_status_instance,
            "recent_clicks": recent_clicks,
        }

    @staticmethod
    def search_urls_with_pagination(query: str, limit: int = 10, page: int = 1):
        urls = Url.objects.filter(
            Q(long_url__icontains=query)
            | Q(short_url__icontains=query)
            | Q(name__icontains=query)
        )

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
    def updated_url_destination(short_url: str, new_destination: str):
        url_instance = Url.objects.get(short_url=short_url)
        url_instance.long_url = new_destination
        url_instance.save()
        return url_instance
