from rest_framework.generics import GenericAPIView
from rest_framework.views import Response, status
from rest_framework.serializers import ValidationError
from api.admin_panel.system.SystemService import SystemService
from api.admin_panel.system.models import SystemConfiguration
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import UserRateThrottle, IPRateThrottle
from api.custom_auth.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from api.admin_panel.system.ConfigService import ConfigService
from .serializers import SystemConfigurationSerializer


class HealthView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_service = SystemService()

    def get(self, request):
        report = self.system_service.get_system_health()
        return Response(report, status=status.HTTP_200_OK)


class ListSystemConfigurationView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request):
        try:
            configs = ConfigService.get_all_configs()
            serializer = SystemConfigurationSerializer(configs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SpecificSystemConfigurationView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def get(self, request, key):
        try:
            value = ConfigService.get_config(key)
            return Response({"key": key, "value": value}, status=status.HTTP_200_OK)
        except SystemConfiguration.DoesNotExist:
            return Response(
                {"error": "key does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, key):
        try:
            data = {"key": key, "value": request.data.get("value")}
            serializer = SystemConfigurationSerializer(data=data, context={"key": key})

            if serializer.is_valid():
                validated_data = serializer.validated_data
                ConfigService.set_config(key, validated_data["value"])

                return Response(
                    {"message": f"Configuration '{key}' updated successfully"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BatchCreateSystemConfigurationView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def post(self, request):
        configs = request.data.get("configs", {})

        validation_errors = {}
        validated_configs = {}

        for key, value in configs.items():
            data = {"key": key, "value": value}
            serializer = SystemConfigurationSerializer(data=data, context={"key": key})

            if serializer.is_valid():
                validated_configs[key] = serializer.validated_data["value"]
            else:
                validation_errors[key] = serializer.errors

        batch_result = ConfigService.batch_set_configs(validated_configs)

        all_errors = validation_errors
        if batch_result.get("errors"):
            all_errors.update(batch_result["errors"])

        response_data = {
            "results": batch_result.get("results", {}),
            "errors": all_errors,
        }

        status_code = status.HTTP_400_BAD_REQUEST if all_errors else status.HTTP_200_OK
        return Response(response_data, status=status_code)
