from django.urls import path

from api.analytics.views import GetUrlSummary, GetUserStats, TopVisitedUrlsView

urlpatterns = [
    path("top-visited/", TopVisitedUrlsView.as_view()),
    path("url-summary/<int:url_id>", GetUrlSummary.as_view()),
    path("user-stats/", GetUserStats.as_view()),
]
