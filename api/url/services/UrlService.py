from api.url.models import Url, UrlStatus
from api.url.services.ShortCodeService import ShortCodeService
from datetime import datetime, timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.models import User


class UrlService:

    @staticmethod
    def create_url(validated_data: dict):
        expiry_date = validated_data.get("expiry_date", None)
        short_url = (
            validated_data["short_url"]
            if validated_data["short_url"] is not None
            else ShortCodeService().get_code()
        )

        is_custom_alias = (
            True
            if "short_url" in validated_data and validated_data["short_url"] is not None
            else False
        )
        user_instance = User.objects.get(pk=validated_data["user"])
        url_instance = Url.objects.create(
            user=user_instance,
            long_url=validated_data["long_url"],
            short_url=short_url,
            expiry_date=expiry_date,
            is_custom_alias=is_custom_alias,
        )
        url_instance.save()
        url_status_instance = UrlStatus.objects.create(url=url_instance)
        url_status_instance.save()
        return url_instance

    def batch_shorten(validated_data: list, user_id: str):
        urls = []
        user_instance = User.objects.get(pk=user_id)
        for url in validated_data:
            short_url = (
                url["short_url"]
                if url["short_url"] is not None
                else ShortCodeService().get_code()
            )

            is_custom_alias = (
                True if "short_url" in url and url["short_url"] is not None else False
            )
            expiry_date = url.get("expiry_date", None)
            try:
                url_instance = Url.objects.create(
                    user=user_instance,
                    long_url=url["long_url"],
                    short_url=short_url,
                    expiry_date=expiry_date,
                    is_custom_alias=is_custom_alias,
                )
                url_instance.save()
                UrlStatus.objects.create(url=url_instance).save()
                urls.append(url_instance)
            except Exception as e:
                urls.append(str(e))
        return urls

    @staticmethod
    def update_url(instance, validated_data):
        for field in ["long_url", "expiry_date"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.updated_at = datetime.now(timezone.utc)
        instance.save()
        return instance

    @staticmethod
    def fetch_urls_with_filter_and_pagination(
        limit: int, page: int, status: UrlStatus.State, user_id: str
    ):
        queryset = Url.objects.select_related("url_status").filter(user=user_id)
        if status:
            queryset = queryset.filter(url_status__state=status)
        queryset = queryset.order_by("-created_at")
        paginator = Paginator(queryset, limit)
        try:
            paginated_urls = paginator.page(page)
        except PageNotAnInteger:
            paginated_urls = paginator.page(1)
        except EmptyPage:
            paginated_urls = paginated_urls(paginator.num_pages)

        return paginated_urls
