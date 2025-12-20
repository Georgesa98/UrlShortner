from datetime import datetime, timezone, timedelta
from api.analytics.models import Visit
from api.url.models import Url
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from collections import defaultdict, Counter
from datetime import datetime, timedelta, timezone
import calendar

User = get_user_model()


class InsightService:
    """Service for platform insights and analytics."""

    @staticmethod
    def get_platform_stats(
        time_range: str = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat,
    ):
        """Get platform statistics for a given time range.

        Args:
            time_range (str): ISO formatted datetime string for the start of the range.

        Returns:
            dict: Statistics including total clicks, new URLs, new users, and unique visits.
        """
        total_clicks = Visit.objects.filter(timestamp__gte=time_range).count()
        new_urls = Url.objects.filter(created_at__gte=time_range).count()
        new_users = User.objects.filter(date_joined__gte=time_range).count()
        unique_visits = Visit.objects.filter(
            timestamp__gte=time_range, new_visitor=True
        ).count()
        return {
            "total_clicks": total_clicks,
            "new_urls": new_urls,
            "new_users": new_users,
            "new_visitors": unique_visits,
        }

    @staticmethod
    def get_growth_metrics():
        """Get growth metrics over the past 10 weeks.

        Returns:
            dict: Growth data for users, URLs, and clicks with weekly breakdowns.
        """
        data_points = 10
        current_date = datetime.now(timezone.utc)
        start_date = current_date - timedelta(weeks=data_points - 1)

        user_growth_data = []
        url_growth_data = []
        click_volume_data = []

        cumulative_users = User.objects.filter(date_joined__lt=start_date).count()
        cumulative_urls = Url.objects.filter(created_at__lt=start_date).count()
        total_clicks = Visit.objects.filter(timestamp__lte=start_date).count()

        for week in range(data_points):
            week_starting = start_date + timedelta(weeks=week)
            new_users = User.objects.filter(
                Q(date_joined__gte=start_date) & Q(date_joined__lte=week_starting)
            ).count()
            cumulative_users += new_users

            new_urls = Url.objects.filter(
                Q(created_at__gte=start_date) & Q(created_at__lte=week_starting)
            ).count()
            cumulative_urls += new_urls

            new_clicks = Visit.objects.filter(
                Q(timestamp__gte=start_date) & Q(timestamp__lte=week_starting)
            ).count()
            total_clicks += new_clicks

            user_growth_data.append(
                {
                    "week_starting": week_starting.strftime("%Y-%m-%d"),
                    "new_users": new_users,
                    "cumulative_users": cumulative_users,
                }
            )
            url_growth_data.append(
                {
                    "week_starting": week_starting.strftime("%Y-%m-%d"),
                    "new_urls": new_urls,
                    "cumulative_users": cumulative_urls,
                }
            )
            click_volume_data.append(
                {
                    "week_starting": week_starting.strftime("%Y-%m-%d"),
                    "total_clicks": total_clicks,
                }
            )
            return {
                "growth_interval": "weekly",
                "data_points": data_points,
                "metrics": {
                    "users_growth": user_growth_data,
                    "urls_growth": url_growth_data,
                    "clicks_volume": click_volume_data,
                },
            }

    @staticmethod
    def get_top_performers(metric: str, limit: int):
        """Get top performers by specified metric.

        Args:
            metric (str): The metric to rank by ('clicks' or 'urls_created').
            limit (int): Number of top performers to return.

        Returns:
            list: Ranked list of top performers with details.
        """
        response = []
        if metric == "clicks":
            top_urls = Url.objects.all().order_by("-visits")[:limit]
            for rank in range(limit):
                response.append(
                    {
                        "rank": rank,
                        "identifier_type": "name",
                        "identifier_value": top_urls[rank].name,
                        "metric": "clicks",
                        "metric_value": top_urls[rank].visits,
                        "details": {
                            "long_url": top_urls[rank].long_url,
                            "short_url": top_urls[rank].short_url,
                        },
                    }
                )
        elif metric == "urls_created":
            top_users = (
                Url.objects.select_related("user")
                .values("user__username")
                .annotate(
                    total_urls=Count("id"),
                    active_urls=Count(
                        "url_status", filter=Q(url_status__state="active")
                    ),
                    expired_urls=Count(
                        "url_status", filter=Q(url_status__state="expired")
                    ),
                )
                .order_by("-total_urls")[:limit]
            )
            for rank in range(limit):
                response.append(
                    {
                        "rank": rank,
                        "identifier_type": "username",
                        "identifier_value": top_users[rank].username,
                        "metric": "urls_created",
                        "metric_value": top_users[rank].total_urls,
                        "details": {
                            "active_urls": top_users[rank].active_urls,
                            "expired_url": top_users[rank].expired_urls,
                        },
                    }
                )
        return response

    @staticmethod
    def get_peak_times():
        """Get peak usage times based on visit data.

        Returns:
            dict: Peak day and hour with average clicks.
        """
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        visits = Visit.objects.filter(timestamp__gte=thirty_days_ago)
        day_counts = defaultdict(int)
        hour_counts = defaultdict(int)
        for visit in visits:
            day_of_week = calendar.day_name[visit.timestamp.weekday()]
            hour = visit.timestamp.hour
            day_counts[day_of_week] += 1
            hour_counts[hour] += 1
        peak_day = max(day_counts, key=day_counts.get) if day_counts else None
        avg_clicks_day = day_counts[peak_day] if peak_day else 0
        peak_hour_int = max(hour_counts, key=hour_counts.get) if hour_counts else None
        if peak_hour_int is not None:
            period = "AM" if peak_hour_int < 12 else "PM"
            display_hour = peak_hour_int if peak_hour_int <= 12 else peak_hour_int - 12
            if display_hour == 0:
                display_hour = 12
            peak_hour = f"{display_hour}:00{period} UTC"
            avg_clicks_hour = hour_counts[peak_hour_int]
        else:
            peak_hour = None
            avg_clicks_hour = 0

        return {
            "day": {"peak_day": peak_day, "avg_clicks": avg_clicks_day},
            "hour": {"peak_hour": peak_hour, "avg_clicks": avg_clicks_hour},
        }

    @staticmethod
    def get_geo_distribution():
        """Get geographic distribution of visits.

        Returns:
            list: Ranked countries by visit count with percentages.
        """
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        visits = Visit.objects.filter(
            timestamp__gte=seven_days_ago, geolocation__isnull=False
        ).exclude(geolocation="")
        country_counts = Counter()
        for visit in visits:
            if visit.geolocation:
                location_parts = visit.geolocation.split(", ")
                country = location_parts[0].strip()
                country_counts[country] += 1
        total_clicks = sum(country_counts.values())
        if total_clicks == 0:
            return []
        leaderboard = []
        sorted_countries = country_counts.most_common()
        for rank, (country, clicks) in enumerate(sorted_countries, start=1):
            percentage = round((clicks / total_clicks) * 100, 2)

            leaderboard.append(
                {
                    "rank": rank,
                    "country": country,
                    "clicks": clicks,
                    "percentage": percentage,
                }
            )

        return leaderboard
