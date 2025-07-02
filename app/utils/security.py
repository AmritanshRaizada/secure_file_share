import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

def generate_secure_token(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_access_token() -> str:
    return generate_secure_token(64)

def is_valid_file_type(filename: str, allowed_types: list) -> bool:
    return any(filename.lower().endswith(ext) for ext in allowed_types)