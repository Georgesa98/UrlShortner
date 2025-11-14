from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView
from api.shortener.models import Url
from django.shortcuts import redirect

from api.shortener.serializers.RedirectSerializer import RedirectSerializer
from api.shortener.serializers.ShortenerSerializer import (
    CreateShortenerSerializer,
)


# Create your views here.


class Shortener(GenericAPIView):

    def post(self, request):
        try:
            serializer = CreateShortenerSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status.HTTP_201_CREATED)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class Redirect(GenericAPIView):

    def get(self, request, token):
        try:
            serializer = RedirectSerializer(data={"short_url": token})
            return redirect(serializer.data["long_url"])
        except Exception as e:
            return Response(str(e), status.HTTP_404_NOT_FOUND)
