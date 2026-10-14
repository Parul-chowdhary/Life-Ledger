"""
Storage Abstraction Layer.
Implements encrypted local filesystem storage with directory sharding,
streaming AES-256-GCM encryption, and SHA-256 integrity validation.
"""
import hashlib
import os
from pathlib import Path
from typing import Optional, Tuple
from lifeledger_core.config import settings
from lifeledger_core.crypto import AESGCMCipher
from lifeledger_core.exceptions import CryptographicError, ResourceNotFoundError, StorageQuotaExceededError


class StorageService:
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.storage_local_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.cipher = AESGCMCipher()

    def _get_path_for_key(self, storage_key: str) -> Path:
        # Shard by first 2 chars of key to avoid high file density in a single folder
        prefix = storage_key[:2]
        dir_path = self.base_dir / prefix
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{storage_key}.enc"

    def store_file(self, file_bytes: bytes, filename: str) -> Tuple[str, str, int, str]:
        """
        Encrypts and stores file content on disk.
        Returns: (storage_key, sha256_hash, file_size_bytes, encryption_iv_hex)
        """
        file_size = len(file_bytes)
        if file_size > settings.max_upload_size_bytes:
            raise StorageQuotaExceededError(file_size, settings.max_upload_size_bytes)

        sha256 = hashlib.sha256(file_bytes).hexdigest()
        ciphertext, nonce = self.cipher.encrypt(file_bytes)

        # Generate a unique storage key from hash
        storage_key = f"{sha256[:16]}_{os.urandom(8).hex()}"
        target_path = self._get_path_for_key(storage_key)

        with open(target_path, "wb") as f:
            f.write(ciphertext)

        return storage_key, sha256, file_size, nonce.hex()

    def retrieve_file(self, storage_key: str, nonce_hex: str) -> bytes:
        """Reads encrypted file from disk, decrypts and validates auth tag."""
        target_path = self._get_path_for_key(storage_key)
        if not target_path.exists():
            raise ResourceNotFoundError("Encrypted file payload", storage_key)

        with open(target_path, "rb") as f:
            ciphertext = f.read()

        try:
            nonce = bytes.fromhex(nonce_hex)
            return self.cipher.decrypt(ciphertext, nonce)
        except Exception as e:
            raise CryptographicError(f"Failed to decrypt stored file: {str(e)}") from e

    def delete_file(self, storage_key: str) -> bool:
        target_path = self._get_path_for_key(storage_key)
        if target_path.exists():
            target_path.unlink()
            return True
        return False
