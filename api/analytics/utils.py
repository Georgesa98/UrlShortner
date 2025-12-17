import hashlib
from api.analytics.models import Visit
from config.settings import SECRET_KEY
import geocoder
import ipaddress


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


def parse_user_agent(user_agent: str) -> dict[str, str]:
    from user_agents import parse

    if not user_agent:
        return {
            "os": "unknown",
            "browser": "unknown",
            "device": "unknown",
            "is_mobile": False,
        }
    try:
        ua = parse(user_agent)
        return {
            "os": ua.os.family.lower(),
            "browser": ua.browser.family.lower(),
            "device": ua.device.family.lower(),
            "is_mobile": ua.is_mobile,
        }
    except Exception:
        return {
            "os": "unknown",
            "browser": "unknown",
            "device": "unknown",
            "is_mobile": False,
        }


def anonymize_ip(ip_address: str) -> str:
    try:
        ip_obj = ipaddress.ip_address(ip_address)

        if isinstance(ip_obj, ipaddress.IPv4Address):
            ip_parts = str(ip_obj).split(".")
            ip_parts[-1] = "0"
            return ".".join(ip_parts)
        elif isinstance(ip_obj, ipaddress.IPv6Address):
            network = ipaddress.IPv6Network(f"{ip_obj}/64", strict=False)
            return str(network.network_address)
        else:
            return ip_address
    except ValueError:
        return ip_address
