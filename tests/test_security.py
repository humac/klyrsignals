"""Tests for encryption and PII stripping."""

import base64
import os
import pytest


class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self, monkeypatch):
        # Generate a test key
        key = os.urandom(32)
        key_b64 = base64.b64encode(key).decode()
        monkeypatch.setenv("ENCRYPTION_KEY", key_b64)

        # Re-import to pick up the env var
        from app.security import encrypt_token, decrypt_token

        # Need to reload settings
        from app.config import Settings
        test_settings = Settings(encryption_key=key_b64)
        monkeypatch.setattr("app.security.settings", test_settings)

        plaintext = "snaptrade-secret-token-12345"
        encrypted = encrypt_token(plaintext)

        assert encrypted != plaintext
        assert len(encrypted) > 0

        decrypted = decrypt_token(encrypted)
        assert decrypted == plaintext

    def test_different_encryptions_differ(self, monkeypatch):
        key = os.urandom(32)
        key_b64 = base64.b64encode(key).decode()

        from app.config import Settings
        test_settings = Settings(encryption_key=key_b64)
        monkeypatch.setattr("app.security.settings", test_settings)

        from app.security import encrypt_token

        enc1 = encrypt_token("same-text")
        enc2 = encrypt_token("same-text")
        # Different nonces should produce different ciphertexts
        assert enc1 != enc2


class TestPIIStripping:
    def test_strips_email(self):
        from app.security import strip_pii

        data = {"name": "John Doe", "email": "john@example.com", "symbol": "VGRO"}
        result = strip_pii(data)
        assert result["email"] == "[REDACTED]"
        assert result["name"] == "[REDACTED]"
        assert result["symbol"] == "VGRO"

    def test_strips_nested_pii(self):
        from app.security import strip_pii

        data = {
            "portfolio": {
                "user_id": "abc-123",
                "positions": [
                    {"symbol": "VGRO", "value": 10000},
                    {"symbol": "XIC", "value": 5000},
                ],
            }
        }
        result = strip_pii(data)
        assert result["portfolio"]["user_id"] == "[REDACTED]"
        assert result["portfolio"]["positions"][0]["symbol"] == "VGRO"

    def test_strips_email_in_strings(self):
        from app.security import strip_pii

        data = {"note": "Contact john@example.com for details"}
        result = strip_pii(data)
        assert "john@example.com" not in result["note"]
        assert "[REDACTED_EMAIL]" in result["note"]

    def test_preserves_financial_data(self):
        from app.security import strip_pii

        data = {
            "symbol": "VGRO.TO",
            "market_value_cents": 1500000,
            "weight_pct": 25.5,
            "sectors": {"Financials": 18.5, "Technology": 14.2},
        }
        result = strip_pii(data)
        assert result["symbol"] == "VGRO.TO"
        assert result["market_value_cents"] == 1500000
        assert result["weight_pct"] == 25.5
        assert result["sectors"]["Financials"] == 18.5
