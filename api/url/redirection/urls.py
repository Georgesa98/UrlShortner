from django.urls import path
from .views import (
    RedirectionRulesListView,
    RedirectionRuleDetailView,
    TestRedirectionView,
)

urlpatterns = [
    path("rules/", RedirectionRulesListView.as_view(), name="redirection-rules-list"),
    path(
        "rules/<int:pk>/",
        RedirectionRuleDetailView.as_view(),
        name="redirection-rule-detail",
    ),
    path("rules/test/", TestRedirectionView.as_view(), name="redirection-rule-test"),
]
