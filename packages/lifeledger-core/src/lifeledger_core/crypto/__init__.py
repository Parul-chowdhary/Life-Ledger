"""
LifeLedger Cryptographic Engine.
Implements AES-256-GCM envelope encryption for stored files,
high-work-factor password hashing, signed access tokens, and timing-safe verification.
"""
import base64
import hashlib
import hmac
import os
import secrets
import time
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from lifeledger_core.exceptions import CryptographicError

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False


class KeyManager:
    """Manages master encryption keys and key derivation."""

    @staticmethod
    def derive_key(master_secret: str, salt: bytes, iterations: int = 100_000) -> bytes:
        """Derives a 256-bit AES key from a passphrase using PBKDF2-HMAC-SHA256."""
        return hashlib.pbkdf2_hmac("sha256", master_secret.encode("utf-8"), salt, iterations, dklen=32)

    @staticmethod
    def generate_random_bytes(length: int = 32) -> bytes:
        return secrets.token_bytes(length)


class AESGCMCipher:
    """High-security authenticated symmetric encryption using AES-256-GCM."""

    def __init__(self, key: Optional[bytes] = None):
        if key is None:
            # 256-bit default or from environment
            master = os.environ.get("LIFELEDGER_MASTER_KEY", "default-dev-master-encryption-key-32b!")
            self.key = hashlib.sha256(master.encode("utf-8")).digest()
        else:
            if len(key) != 32:
                raise CryptographicError("AES-256 requires exactly a 32-byte key")
            self.key = key
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Encrypts plaintext bytes with AES-256-GCM.
        Returns: (ciphertext_with_auth_tag, nonce_iv)
        """
        try:
            nonce = secrets.token_bytes(12)  # Standard 96-bit nonce for AES-GCM
            ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data)
            return ciphertext, nonce
        except Exception as e:
            raise CryptographicError(f"Encryption failed: {str(e)}") from e

    def decrypt(self, ciphertext: bytes, nonce: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypts AES-256-GCM ciphertext using the nonce and validates authentication tag.
        """
        try:
            return self.aesgcm.decrypt(nonce, ciphertext, associated_data)
        except Exception as e:
            raise CryptographicError(f"Decryption / Authentication tag verification failed: {str(e)}") from e

    def encrypt_string(self, text: str) -> str:
        """Helper to encrypt string and return URL-safe base64 encoded string."""
        ct, nonce = self.encrypt(text.encode("utf-8"))
        combined = nonce + ct
        return base64.urlsafe_b64encode(combined).decode("ascii")

    def decrypt_string(self, token: str) -> str:
        """Helper to decrypt URL-safe base64 string back to plaintext."""
        try:
            raw = base64.urlsafe_b64decode(token.encode("ascii"))
            nonce = raw[:12]
            ct = raw[12:]
            decrypted = self.decrypt(ct, nonce)
            return decrypted.decode("utf-8")
        except Exception as e:
            raise CryptographicError(f"Failed to decrypt string: {str(e)}") from e


class PasswordHasher:
    """Secure password hashing using bcrypt with PBKDF2 fallback."""

    @staticmethod
    def hash_password(password: str) -> str:
        if HAS_BCRYPT:
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("ascii")
        else:
            salt = secrets.token_hex(16)
            key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 100_000)
            return f"pbkdf2:sha256:100000${salt}${key.hex()}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        try:
            if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
                return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("ascii"))
            elif hashed_password.startswith("pbkdf2:sha256:"):
                parts = hashed_password.split("$")
                salt = parts[1]
                expected_hex = parts[2]
                computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 100_000)
                return hmac.compare_digest(computed.hex(), expected_hex)
            return False
        except Exception:
            return False


class TokenSigner:
    """Generates and verifies cryptographically signed tokens with expiration (e.g. for password reset, shared links)."""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret = (secret_key or os.environ.get("SECRET_KEY", "lifeledger-default-secret-key-2026")).encode("utf-8")

    def create_token(self, payload: str, expires_in_seconds: int = 900) -> str:
        expire_at = int(time.time()) + expires_in_seconds
        message = f"{payload}:{expire_at}"
        signature = hmac.new(self.secret, message.encode("utf-8"), hashlib.sha256).hexdigest()
        token = f"{message}:{signature}"
        return base64.urlsafe_b64encode(token.encode("utf-8")).decode("ascii")

    def verify_token(self, token: str) -> Optional[str]:
        try:
            raw = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
            payload, expire_at_str, signature = raw.rsplit(":", 2)
            expire_at = int(expire_at_str)
            if time.time() > expire_at:
                return None  # Expired
            message = f"{payload}:{expire_at}"
            expected_sig = hmac.new(self.secret, message.encode("utf-8"), hashlib.sha256).hexdigest()
            if hmac.compare_digest(signature, expected_sig):
                return payload
            return None
        except Exception:
            return None
