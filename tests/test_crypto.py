"""
Automated Cryptographic Unit Tests.
Verifies AES-256-GCM envelope encryption, authentication tags,
password hashing, and signed token expiration.
"""
import pytest
from lifeledger_core.crypto import AESGCMCipher, KeyManager, PasswordHasher, TokenSigner
from lifeledger_core.exceptions import CryptographicError


def test_aes_gcm_encryption_roundtrip():
    cipher = AESGCMCipher()
    secret_text = b"Confidential passport document stream #12345"
    
    ciphertext, nonce = cipher.encrypt(secret_text)
    assert ciphertext != secret_text
    assert len(nonce) == 12

    decrypted = cipher.decrypt(ciphertext, nonce)
    assert decrypted == secret_text


def test_aes_gcm_tampered_ciphertext_fails():
    cipher = AESGCMCipher()
    ciphertext, nonce = cipher.encrypt(b"Legitimate document payload")
    
    # Tamper with byte
    tampered = bytearray(ciphertext)
    tampered[5] ^= 0xFF

    with pytest.raises(CryptographicError):
        cipher.decrypt(bytes(tampered), nonce)


def test_aes_gcm_string_helper():
    cipher = AESGCMCipher()
    orig = "My Secret Insurance Policy #88912"
    token = cipher.encrypt_string(orig)
    assert token != orig
    assert cipher.decrypt_string(token) == orig


def test_password_hasher_verification():
    pwd = "UltraSecurePassword2026!"
    hashed = PasswordHasher.hash_password(pwd)
    
    assert PasswordHasher.verify_password(pwd, hashed) is True
    assert PasswordHasher.verify_password("WrongPassword!", hashed) is False


def test_token_signer_valid_and_expired():
    signer = TokenSigner("test-secret-key-123")
    token = signer.create_token("user_123:action_reset", expires_in_seconds=60)
    
    payload = signer.verify_token(token)
    assert payload == "user_123:action_reset"

    # Expired token test
    expired_token = signer.create_token("user_123:action_reset", expires_in_seconds=-10)
    assert signer.verify_token(expired_token) is None
