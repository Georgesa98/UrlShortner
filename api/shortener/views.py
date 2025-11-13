from rest_framework.views import APIView, Response, status
from api.shortener.models import Url
from django.shortcuts import redirect
import secrets
import urllib.parse


# Create your views here.
def generator():
    token = secrets.token_bytes(4)
    return token.hex()


def urlChecker(url):
    try:
        urllib.parse.urlparse(url)
        return True
    except:
        return False


class Shortener(APIView):
    def post(self, request):
        try:
            if urlChecker(request.data["url"]):
                url = Url.objects.create(
                    long_url=request.data["url"], short_url=generator()
                )
                return Response(
                    {"response": request.get_host() + "/" + url.short_url},
                    status.HTTP_200_OK,
                )
            else:
                return Response("please enter a valid url", status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


class Redirect(APIView):
    def get(self, request, token):
        try:
            url = Url.objects.get(short_url=token)
            return redirect(url.long_url)
        except Exception as e:
            return Response(str(e), status.HTTP_404_NOT_FOUND)
