from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from api.custom_auth.permissions import IsAdmin
from api.url.permissions import IsUrlOwner
from api.throttling import IPRateThrottle, UserRateThrottle
from config.utils.responses import SuccessResponse, ErrorResponse
from .RedirectionService import RedirectionService
from .serializers import RedirectionRuleSerializer, TestRedirectionSerializer
from api.url.models import Url


class RedirectionRulesListView(GenericAPIView):
    serializer_class = RedirectionRuleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [IPRateThrottle, UserRateThrottle]

    def get_queryset(self):
        url_id = self.request.query_params.get("url_id")
        return RedirectionService.get_rules(url_id=url_id)

    def get(self, request):
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return SuccessResponse(
                data=serializer.data,
                message="Redirection rules retrieved successfully",
                status=200,
            )
        except Exception as e:
            return ErrorResponse(message=str(e), status=500)

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            rule = RedirectionService.create_rule(serializer.validated_data)
            serializer = self.get_serializer(rule)
            return SuccessResponse(
                data=serializer.data,
                message="Redirection rule created successfully",
                status=201,
            )
        except ValueError as e:
            return ErrorResponse(message=str(e), status=400)
        except Exception as e:
            return ErrorResponse(message=str(e), status=400)


class RedirectionRuleDetailView(GenericAPIView):
    serializer_class = RedirectionRuleSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    throttle_classes = [IPRateThrottle, UserRateThrottle]

    def get(self, request, pk):
        try:
            instance = RedirectionService.get_rule_by_id(pk)
            serializer = self.get_serializer(instance)
            return SuccessResponse(
                data=serializer.data,
                message="Redirection rule retrieved successfully",
                status=200,
            )
        except ValueError as e:
            return ErrorResponse(message=str(e), status=404)
        except Exception as e:
            return ErrorResponse(message=str(e), status=500)

    def put(self, request, pk):
        try:
            instance = RedirectionService.get_rule_by_id(pk)
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            rule = RedirectionService.update_rule(instance, serializer.validated_data)
            serializer = self.get_serializer(rule)
            return SuccessResponse(
                data=serializer.data,
                message="Redirection rule updated successfully",
                status=200,
            )
        except ValueError as e:
            return ErrorResponse(message=str(e), status=400)
        except Exception as e:
            return ErrorResponse(message=str(e), status=400)

    def patch(self, request, pk):
        try:
            instance = RedirectionService.get_rule_by_id(pk)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            rule = RedirectionService.update_rule(instance, serializer.validated_data)
            serializer = self.get_serializer(rule)
            return SuccessResponse(
                data=serializer.data,
                message="Redirection rule updated successfully",
                status=200,
            )
        except ValueError as e:
            return ErrorResponse(message=str(e), status=400)
        except Exception as e:
            return ErrorResponse(message=str(e), status=400)

    def delete(self, request, pk):
        try:
            instance = RedirectionService.get_rule_by_id(pk)
            RedirectionService.delete_rule(instance)
            return SuccessResponse(
                message="Redirection rule deleted successfully",
                status=204,
            )
        except ValueError as e:
            return ErrorResponse(message=str(e), status=404)
        except Exception as e:
            return ErrorResponse(message=str(e), status=400)


class TestRedirectionView(GenericAPIView):
    serializer_class = TestRedirectionSerializer
    permission_classes = [IsAuthenticated, IsUrlOwner]
    throttle_classes = [IPRateThrottle, UserRateThrottle]

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            url_id = validated_data.pop("url_id")

            try:
                url = Url.objects.get(id=url_id)
            except Url.DoesNotExist:
                return ErrorResponse(message="URL not found", status=404)

            try:
                self.check_object_permissions(request, url)
            except Exception:
                return ErrorResponse(
                    message="You don't have permission to test rules for this URL",
                    status=403,
                )

            service = RedirectionService()
            matched_rule = service.test_evaluate_rules(url_id, validated_data)

            if matched_rule:
                response_data = {
                    "matched_rule": {
                        "id": matched_rule.id,
                        "name": matched_rule.name,
                        "target_url": matched_rule.target_url,
                        "priority": matched_rule.priority,
                        "conditions": matched_rule.conditions,
                    },
                    "target_url": matched_rule.target_url,
                    "test_context": validated_data,
                }
                message = "Rule matched successfully"
            else:
                response_data = {
                    "matched_rule": None,
                    "target_url": url.long_url,
                    "test_context": validated_data,
                }
                message = "No rule matched the provided context"

            return SuccessResponse(
                data=response_data,
                message=message,
                status=200,
            )
        except ValidationError as e:
            return ErrorResponse(message=str(e), status=400)
        except ValueError as e:
            return ErrorResponse(message=str(e), status=400)
        except Exception as e:
            return ErrorResponse(message=str(e), status=500)
