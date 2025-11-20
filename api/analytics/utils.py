import hashlib
from api.analytics.models import Visit
from config.settings import SECRET_KEY


def hash_ip(ip: str) -> str:
    raw = f"{SECRET_KEY}:{ip}".encode()
    return hashlib.sha256(raw).hexdigest()


def get_ip_address(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def ip_address_match(ip: str) -> bool:
    hashed_ip = hash_ip(ip)
    return Visit.objects.filter(hashed_ip=hashed_ip).exists()
