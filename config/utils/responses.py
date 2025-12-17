from rest_framework.views import Response


class SuccessResponse(Response):
    def __init__(self, data=None, message=None, status=None, **kwargs):
        response_data = {"success": True, "message": message, "data": data}
        super().__init__(response_data, status, **kwargs)


class ErrorResponse(Response):
    def __init__(
        self, message="An error occurred", errors=None, data=None, status=None, **kwargs
    ):
        response_data = {
            "success": False,
            "message": message,
        }
        if errors:
            response_data["errors"] = errors
        if data is not None:
            response_data["data"] = data

        super().__init__(response_data, status, **kwargs)
