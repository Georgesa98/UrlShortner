from django.urls import path, include
from api.admin_panel.views import (
    GetUserUrlsView,
    BulkUrlDeletionView,
    BulkFlagUrlView,
    GetUrlDetailsView,
    SearchUrlsView,
    UpdateUrlDestinationView,
    GetUsersView,
    ToggleBanUserView,
    BulkUserDeletionView,
    GetUserDetailsView,
    SearchUsersView,
)

urlpatterns = [
    # URL Management endpoints
    path("user/urls/<int:user_id>/", GetUserUrlsView.as_view(), name="get-user-urls"),
    path("urls/bulk-delete/", BulkUrlDeletionView.as_view(), name="bulk-url-deletion"),
    path("urls/bulk-flag/", BulkFlagUrlView.as_view(), name="bulk-flag-url"),
    path(
        "url/destination/<str:short_url>/",
        UpdateUrlDestinationView.as_view(),
        name="update-url-destination",
    ),
    path(
        "url/details/<int:url_id>/", GetUrlDetailsView.as_view(), name="get-url-details"
    ),
    path("urls/search/", SearchUrlsView.as_view(), name="search-urls"),
    # User Management endpoints
    path("users/", GetUsersView.as_view(), name="get-users"),
    path(
        "user/<int:user_id>/ban/", ToggleBanUserView.as_view(), name="toggle-ban-user"
    ),
    path(
        "users/bulk-delete/", BulkUserDeletionView.as_view(), name="bulk-user-deletion"
    ),
    path(
        "user/details/<int:user_id>/",
        GetUserDetailsView.as_view(),
        name="get-user-details",
    ),
    path("users/search/", SearchUsersView.as_view(), name="search-users"),
    # Existing module endpoints
    path("system/", include("api.admin_panel.system.urls")),
    path("insight/", include("api.admin_panel.insight.urls")),
    path("audit/", include("api.admin_panel.audit.urls")),
    path("fraud/", include("api.admin_panel.fraud.urls")),
]
