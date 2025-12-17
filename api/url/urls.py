from django.urls import path, include

from api.url.views import (
    BatchShorten,
    GenerateQrcode,
    ListUrlsView,
    Redirect,
    Shortener,
    SpecificUrl,
)

urlpatterns = [
    path("shorten/", Shortener.as_view()),
    path("batch-shorten/", BatchShorten.as_view()),
    path("redirect/<str:short_url>/", Redirect.as_view()),
    path("qr/<str:short_url>/", GenerateQrcode.as_view()),
    path(
        "<str:short_url>/",
        SpecificUrl.as_view(),
    ),
    path("", ListUrlsView.as_view()),
    path("redirection/", include("api.url.redirection.urls")),
]
