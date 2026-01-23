from .views import (
    GetUsersView,
    ToggleBanUserView,
    BulkUserDeletionView,
    GetUserDetailsView,
)
from django.urls import path

urlpatterns = [
    path("", GetUsersView.as_view(), name="get-users"),
    path("<int:user_id>/ban/", ToggleBanUserView.as_view(), name="toggle-ban-user"),
    path("bulk-delete/", BulkUserDeletionView.as_view(), name="bulk-user-deletion"),
    path(
        "details/<int:user_id>/",
        GetUserDetailsView.as_view(),
        name="get-user-details",
    ),
]
