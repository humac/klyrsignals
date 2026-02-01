"""Security utilities: AES-256-GCM encryption and PII stripping."""

import base64
import os
import re

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings


def _get_key() -> bytes:
    """Get or generate the AES-256 encryption key."""
    key_b64 = settings.encryption_key
    if not key_b64:
        raise ValueError("ENCRYPTION_KEY environment variable is not set")
    return base64.b64decode(key_b64)


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token using AES-256-GCM. Returns base64(nonce + ciphertext)."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_token(encrypted: str) -> str:
    """Decrypt a token encrypted with encrypt_token."""
    key = _get_key()
    raw = base64.b64decode(encrypted)
    nonce = raw[:12]
    ciphertext = raw[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")


def strip_pii(data: dict) -> dict:
    """Remove personally identifiable information before sending to cloud AI.

    Strips: email addresses, names, account numbers, user IDs.
    Keeps: symbols, values, percentages, analysis data.
    """
    pii_keys = {"email", "name", "first_name", "last_name", "user_id", "account_number",
                "snaptrade_user_id", "snaptrade_user_secret", "snaptrade_authorization_id",
                "snaptrade_account_id"}

    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    def _strip(obj: dict | list | str | int | float | None) -> dict | list | str | int | float | None:
        if isinstance(obj, dict):
            return {
                k: "[REDACTED]" if k.lower() in pii_keys else _strip(v)
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [_strip(item) for item in obj]
        if isinstance(obj, str):
            return email_pattern.sub("[REDACTED_EMAIL]", obj)
        return obj

    return _strip(data)
