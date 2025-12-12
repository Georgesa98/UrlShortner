from django.urls import path
from api.admin_panel.insight.views import (
    PlatformStatsView,
    GrowthMetricsView,
    TopPerformersView,
    PeakTimesView,
    GeoDistributionView,
)

urlpatterns = [
    path("platform-stats/", PlatformStatsView.as_view()),
    path("growth-metric/", GrowthMetricsView.as_view()),
    path("top-performers/", TopPerformersView.as_view()),
    path("peak-times/", PeakTimesView.as_view()),
    path("geo-dist/", GeoDistributionView.as_view()),
]
