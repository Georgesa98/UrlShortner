from django.urls import path

from api.analytics.views import GetUrlSummary, TopVisitedUrlsView

urlpatterns = [
    path("top-visited/", TopVisitedUrlsView.as_view()),
    path("url-summary/<str:url_id>", GetUrlSummary.as_view()),
]
