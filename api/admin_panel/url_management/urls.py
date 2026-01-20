from .views import (
    BulkUrlDeletionView,
    BulkFlagUrlView,
    GetUrlsStatsView,
    GetUserUrlsView,
    ListUrlsView,
    UpdateUrlDestinationView,
    GetUrlDetailsView,
    SearchUrlsView,
)
from django.urls import path

urlpatterns = [
    path("stats/", GetUrlsStatsView.as_view(), name="get-urls-stats"),
    path("bulk-delete/", BulkUrlDeletionView.as_view(), name="bulk-url-deletion"),
    path("bulk-flag/", BulkFlagUrlView.as_view(), name="bulk-flag-url"),
    path("", ListUrlsView.as_view(), name="list-urls"),
    path(
        "destination/<str:short_url>/",
        UpdateUrlDestinationView.as_view(),
        name="update-url-destination",
    ),
    path("details/<int:url_id>/", GetUrlDetailsView.as_view(), name="get-url-details"),
    path("search/", SearchUrlsView.as_view(), name="search-urls"),
    path("user/<int:user_id>/", GetUserUrlsView.as_view(), name="get-user-urls"),
]
