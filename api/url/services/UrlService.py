from api.url.models import Url, UrlStatus
from api.url.services.ShortCodeService import ShortCodeService
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
User = get_user_model()


class UrlService:
    @staticmethod
    def create_url(validated_data: dict) -> object:
        """Create a new URL instance with short code generation and status.

        Args:
            validated_data (dict): Validated data containing long_url, user, short_url (optional), expiry_date (optional).

        Returns:
            Url: The created URL instance with associated UrlStatus.

        Raises:
            User.DoesNotExist: If the specified user does not exist.
        """
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
        url = Url.objects.create(
            user=user_instance,
            long_url=validated_data["long_url"],
            short_url=short_url,
            expiry_date=expiry_date,
            is_custom_alias=is_custom_alias,
        )
        url.save()
        url_status = UrlStatus.objects.create(url=url)
        url_status.save()
        url_instance = Url.objects.select_related("url_status").get(id=url.id)
        return url_instance

    @staticmethod
    def batch_shorten(validated_data: list, user_id: str) -> list:
        """Create multiple URLs in batch with short code generation.

        Args:
            validated_data (list): List of validated URL data dicts, each containing long_url, short_url (optional), expiry_date (optional).
            user_id (str): ID of the user creating the URLs.

        Returns:
            list: List of created Url instances or error strings for failed creations.
        """
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
        url_instances = list(
            Url.objects.filter(id__in=[item.id for item in urls]).select_related(
                "url_status", "user"
            )
        )
        return url_instances

    @staticmethod
    def update_url(instance, validated_data) -> object:
        """Update an existing URL instance with provided data.

        Args:
            instance (Url): The URL instance to update.
            validated_data (dict): Validated data containing fields to update (long_url, expiry_date).

        Returns:
            Url: The updated URL instance.
        """
        for field in ["long_url", "expiry_date"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.updated_at = timezone.now()
        instance.save()
        return instance

    @staticmethod
    def fetch_urls_with_filter_and_pagination(
        limit: int, page: int, status: UrlStatus.State, user_id: str, date_created_order: str, query: str
    ) -> object:
        """Fetch paginated URLs for a user with optional status filtering.

        Args:
            limit (int): Number of URLs per page.
            page (int): Page number to retrieve.
            status (UrlStatus.State): Optional status filter.
            user_id (str): ID of the user.
            date_created_order (str): Ordering field for date created.
            query (str): Search query for long_url, short_url, or name.

        Returns:
            Page: Paginated page object containing Url instances.
        """
        queryset = Url.objects.select_related("url_status", "user").filter(
            user__id=user_id
        )
        if query:
            queryset = queryset.filter(
                Q(long_url__icontains=query)
                | Q(short_url__icontains=query)
                | Q(name__icontains=query)
            )
        if status:
            queryset = queryset.filter(url_status__state=status)
        if date_created_order:
            order = "-created_at" if date_created_order == "DESC" else "created_at"
            queryset = queryset.order_by(order)
        paginator = Paginator(queryset, limit)
        try:
            paginated_urls = paginator.page(page)
        except PageNotAnInteger:
            paginated_urls = paginator.page(1)
        except EmptyPage:
            paginated_urls = paginated_urls(paginator.num_pages)

        return paginated_urls
