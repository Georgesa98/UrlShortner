import urllib
import secrets


def generator():
    token = secrets.token_bytes(4)
    return token.hex()


def urlChecker(url):
    try:
        urllib.parse.urlparse(url)
        return True
    except:
        return False
