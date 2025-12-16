def get_throttle_rates():
    """Get throttle rates from config service, fallback to defaults"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return {
            "ip": ConfigService.get_config("rate_limit_ip", "100/hour"),
            "user": ConfigService.get_config("rate_limit_user", "1000/hour"),
        }
    except Exception:
        return {"ip": "100/hour", "user": "1000/hour"}


def get_jwt_access_token_minutes():
    """Get JWT access token lifetime in minutes from config service"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return ConfigService.get_config("jwt_access_token_minutes", 5)
    except Exception:
        return 5


def get_short_code_length():
    """Get short code length from config service"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return ConfigService.get_config("short_code_length", 8)
    except Exception:
        return 8


def get_short_code_pool_size():
    """Get short code pool size from config service"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return ConfigService.get_config("short_code_pool_size", 10000)
    except Exception:
        return 10000


def get_analytics_track_ip():
    """Get whether to track IP addresses in analytics"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return ConfigService.get_config("analytics_track_ip", True)
    except Exception:
        return True


def get_max_urls_per_user():
    """Get maximum URLs per user limit"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return ConfigService.get_config("max_urls_per_user", 100)
    except Exception:
        return 100


def get_url_mapping_cache_timeout():
    """Get URL mapping cache timeout"""
    try:
        from api.admin_panel.system.ConfigService import ConfigService

        return ConfigService.get_config("url_mapping_cache_timeout", 3600)
    except Exception:
        return 3600
