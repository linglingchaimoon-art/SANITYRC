from cryptography.fernet import Fernet

from app.config import ENCRYPTION_KEY


if not ENCRYPTION_KEY:
    raise RuntimeError("ENCRYPTION_KEY is missing")

fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()