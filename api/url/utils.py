from io import BytesIO
import secrets
from validators import url as validate_url, ValidationError
import qrcode


def generate_qrcode(url: str) -> memoryview:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getbuffer()


def urlChecker(url: str) -> bool:
    is_valid = validate_url(url)
    if isinstance(is_valid, ValidationError):
        return False
    return True
