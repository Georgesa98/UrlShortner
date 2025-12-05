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
