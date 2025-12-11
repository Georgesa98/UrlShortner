from rest_framework.generics import GenericAPIView
from rest_framework.views import Response, status
from api.admin_panel.services.SystemService import SystemService
from api.custom_auth.authentication import CookieJWTAuthentication
from api.throttling import UserRateThrottle, IPRateThrottle
from api.custom_auth.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class HealthView(GenericAPIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [UserRateThrottle, IPRateThrottle]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.system_service = SystemService()

    def get(self, request):
        report = self.system_service.get_system_health()
        return Response(report, status.HTTP_200_OK)
