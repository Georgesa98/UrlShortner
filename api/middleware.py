from django.utils.deprecation import MiddlewareMixin
from api.admin_panel.audit.AuditService import AuditService
from api.admin_panel.audit.models import AuditLog
from api.analytics.utils import anonymize_ip, get_ip_address
from django.urls import resolve
from django.http import HttpRequest


class RateLimitHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(request, "throttle_metadata"):
            metadata = request.throttle_metadata
            response["X-RateLimit-Limit"] = str(metadata["limit"])
            response["X-RateLimit-Remaining"] = str(metadata["remaining"])
            response["X-RateLimit-Reset"] = str(metadata["reset"])

        return response


class AuditMiddleware(MiddlewareMixin):
    ALLOWED_METHODS = ["POST", "PUT", "PATCH", "DELETE"]

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if self.is_method_allowed(request.method):
            if request.method in self.ALLOWED_METHODS:
                request.original_body = request.body

            user_id = self.get_user_id(request)
            ip_address = get_ip_address(request)
            action_type = self.determine_action_type(request)

            request.audit_info = {
                "user_id": user_id,
                "ip_address": ip_address,
                "original_method": request.method,
                "original_path": request.path,
                "action_type": action_type,
            }

    def process_response(self, request, response):
        if hasattr(request, "audit_info"):
            user_id = request.audit_info["user_id"]
            ip_address = request.audit_info["ip_address"]
            action_type = request.audit_info["action_type"]
            content_type = self.get_content_type(request)
            content_id = self.get_content_id(request)

            AuditService.initiate_log(
                action=action_type,
                ip_address=anonymize_ip(ip_address),
                user_id=user_id,
            )

        return response

    def is_method_allowed(self, method):
        return method.upper() in self.ALLOWED_METHODS

    def get_user_id(self, request):
        if hasattr(request, "_force_auth_user") and request._force_auth_user:
            return request._force_auth_user.id

        try:
            user = request.user
            if user and hasattr(user, "is_authenticated"):
                if user.is_authenticated:
                    return getattr(user, "id", None)
        except AttributeError:
            pass

        return None

    def determine_action_type(self, request):
        method = request.method.upper()
        action_map = {
            "POST": "CREATE",
            "PUT": "UPDATE",
            "PATCH": "UPDATE",
            "DELETE": "DELETE",
        }
        return action_map.get(method, "OTHER")

    def get_content_type(self, request):
        try:
            resolver_match = resolve(request.path_info)
            if hasattr(resolver_match, "view_name"):
                return resolver_match.view_name
            elif hasattr(resolver_match.func, "model"):
                return resolver_match.func.model._meta.model_name
            else:
                return (
                    f"{resolver_match.app_name}:{resolver_match.url_name}"
                    if resolver_match.app_name
                    else resolver_match.url_name
                )
        except:
            return "unknown"

    def get_content_id(self, request):
        try:
            resolver_match = resolve(request.path_info)
            for key in ["id", "pk", "short_url", "slug", "uuid"]:
                if key in resolver_match.kwargs:
                    return str(resolver_match.kwargs[key])
            return "unknown"
        except:
            return "unknown"
