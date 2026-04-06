import math
import re

from bson import ObjectId

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(email or ""))


def password_meets_policy(password: str) -> bool:
    return (
        len(password or "") >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"[0-9]", password)
    )


def clean_text(value: str, max_length: int) -> str:
    return (value or "").strip()[:max_length]


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def to_object_id(value: str):
    if not value or not ObjectId.is_valid(value):
        return None
    return ObjectId(value)


def human_size(size: int) -> str:
    if size <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    power = min(int(math.log(size, 1024)), len(units) - 1)
    scaled = size / (1024**power)
    return f"{scaled:.1f} {units[power]}"


def short_ciphertext(value: str, limit: int = 96) -> str:
    if not value:
        return ""
    return value if len(value) <= limit else f"{value[:limit]}..."
