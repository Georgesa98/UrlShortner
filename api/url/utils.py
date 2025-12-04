import secrets
from validators import url as validate_url, ValidationError


def generator():
    token = secrets.token_bytes(4)
    return token.hex()


def urlChecker(url):
    is_valid = validate_url(url)
    if isinstance(is_valid, ValidationError):
        return False
    return True
