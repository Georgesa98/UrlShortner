from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView
from config.utils.responses import SuccessResponse, ErrorResponse
from api.throttling import IPRateThrottle, UserRateThrottle
from api.custom_auth.authentication import CookieJWTAuthentication
from rest_framework.permissions import IsAuthenticated
from api.url.models import Url
from api.url.link_rot.LinkRotService import LinkRotService
from django.shortcuts import get_object_or_404
from .serializers import (
    HealthCheckRequestSerializer,
    HealthCheckResultSerializer,
)


class CheckUrlHealthView(GenericAPIView):
    """
    Check the health of a single URL by ID
    """

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, url_id):
        try:
            return Url.objects.select_related("url_status").get(
                id=url_id, user=self.request.user
            )
        except Url.DoesNotExist:
            return None

    def post(self, request, url_id):
        """
        Check the health of a specific URL
        """
        try:
            url_instance = self.get_object(url_id)
            if url_instance is None:
                return ErrorResponse(
                    message="URL not found", status=status.HTTP_404_NOT_FOUND
                )
            service = LinkRotService()
            health_result = service.check_url_health(url_instance)
            service.update_url_status(
                url_id, health_result["status"], health_result["error"]
            )

            service.close()

            result_serializer = HealthCheckResultSerializer(data=health_result)
            if result_serializer.is_valid():
                validated_data = result_serializer.validated_data
            else:
                validated_data = health_result

            return SuccessResponse(
                data=validated_data,
                message="URL health check completed successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CheckBatchHealthView(GenericAPIView):
    """
    Check the health of a batch of URLs
    """

    throttle_classes = [IPRateThrottle, UserRateThrottle]
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Check the health of multiple URLs
        Expected payload: {"url_ids": [1, 2, 3, ...]}
        """
        try:
            serializer = HealthCheckRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return ErrorResponse(
                    message="Invalid input data",
                    errors=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                )

            url_ids = serializer.validated_data["url_ids"]
            user_urls = Url.objects.filter(
                id__in=url_ids, user=request.user
            ).values_list("id", flat=True)

            user_url_ids = list(user_urls)

            if len(user_url_ids) != len(url_ids):
                return ErrorResponse(
                    message="Some URLs do not belong to the authenticated user",
                    status=status.HTTP_403_FORBIDDEN,
                )

            service = LinkRotService()
            health_results = service.check_batch_health(user_url_ids)
            status_updates = []
            for result in health_results:
                status_updates.append(
                    {
                        "url_id": result["url_id"],
                        "status": result["status"],
                        "reason": result["error"],
                    }
                )

            update_results = service.bulk_update_statuses(status_updates)
            service.close()
            validated_results = []
            for result in health_results:
                result_serializer = HealthCheckResultSerializer(data=result)
                if result_serializer.is_valid():
                    validated_results.append(result_serializer.validated_data)
                else:
                    validated_results.append(result)

            return SuccessResponse(
                data={
                    "health_results": validated_results,
                    "update_results": update_results,
                },
                message="Batch health check completed successfully",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ErrorResponse(
                message=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
