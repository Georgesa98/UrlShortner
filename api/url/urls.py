from django.urls import path

from api.url.views import Redirect, Shortener, SpecificUrl

urlpatterns = [
    path("shorten/", Shortener.as_view()),
    path(
        "<str:short_url>",
        SpecificUrl.as_view(),
    ),
    path("redirect/<str:short_url>", Redirect.as_view()),
]
