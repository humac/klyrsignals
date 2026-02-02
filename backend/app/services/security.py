from cryptography.fernet import Fernet
import os

class SecurityService:
    _cipher = None

    @classmethod
    def _get_cipher(cls):
        if cls._cipher:
            return cls._cipher
        
        # Read key lazily
        key = os.getenv("FERNET_KEY")
        
        if not key or key.startswith("PLEASE_CHANGE"):
            # Fallback for dev/test if key not set, OR raise error in prod
            # For this project, we'll generate a temp key if none exists to prevent crash,
            # but log warning.
            print("WARNING: methods using encryption called without valid FERNET_KEY.")
            # In a real app, maybe raise Exception.
            # For now, let's assume if it is missing we can't encrypt.
            return None
            
        try:
            cls._cipher = Fernet(key)
        except Exception as e:
            print(f"Error initializing Fernet: {e}")
            return None
        return cls._cipher

    @staticmethod
    def encrypt_token(raw_token: str) -> str:
        """
        Encrypts a raw token string. Returns base64 encoded string.
        """
        if not raw_token:
            return None
        
        cipher = SecurityService._get_cipher()
        if not cipher:
            raise ValueError("Encryption service not configured correctly (Missing FERNET_KEY)")
            
        return cipher.encrypt(raw_token.encode()).decode()

    @staticmethod
    def decrypt_token(enc_token: str) -> str:
        """
        Decrypts an encrypted token string.
        """
        if not enc_token:
            return None

        cipher = SecurityService._get_cipher()
        if not cipher:
            raise ValueError("Encryption service not configured correctly")
            
        return cipher.decrypt(enc_token.encode()).decode()
