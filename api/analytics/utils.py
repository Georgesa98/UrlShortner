import hashlib
from api.analytics.models import Visit
from config.settings import SECRET_KEY
import geocoder


def hash_ip(ip: str) -> str:
    raw = f"{SECRET_KEY}:{ip}".encode()
    return hashlib.sha256(raw).hexdigest()


def get_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def ip_address_match(hashed_ip: str) -> bool:
    return Visit.objects.filter(hashed_ip=hashed_ip).exists()


def convert_ip_to_location(ip: str) -> str:
    geo = geocoder.ip(ip)
    if geo.country:
        return geo.country
    else:
        return "Unknown"


def parse_user_agent(user_agent: str) -> dict[str, dict]:
    from user_agents import parse

    if not user_agent:
        return {"os": "Unknown", "browser": "Unknown", "device": "Unknown"}
    ua = parse(user_agent)
    return {"os": ua.os.family, "browser": ua.browser.family, "device": ua.device.brand}
