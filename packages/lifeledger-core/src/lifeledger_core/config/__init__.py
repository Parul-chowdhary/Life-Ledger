"""
LifeLedger Configuration System.
Provides type-safe environment configuration with production defaults.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent


class LifeLedgerSettings(BaseSettings):
    """Central settings model for LifeLedger application."""

    # Environment & General
    app_env: str = Field(default="development", description="development | testing | production")
    debug: bool = Field(default=True)
    secret_key: str = Field(default="lifeledger-super-secure-production-secret-key-2026-xyz!")

    # Server Configuration
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=5000)

    # Database
    database_url: str = Field(
        default=f"sqlite:///{WORKSPACE_ROOT / 'instance' / 'lifeledger.db'}",
        description="Database connection URI"
    )

    # Storage Backend
    storage_backend: str = Field(default="local", description="local | s3")
    storage_local_dir: str = Field(
        default=str(WORKSPACE_ROOT / "var" / "storage"),
        description="Base path for local encrypted document storage"
    )

    # Cryptography
    master_encryption_key: str = Field(
        default="lifeledger-master-envelope-key-32b!",
        description="Master 256-bit AES envelope key"
    )

    # Storage Quotas
    default_workspace_quota_bytes: int = Field(
        default=5 * 1024 * 1024 * 1024,  # 5 GB
        description="Default quota per workspace in bytes"
    )
    max_upload_size_bytes: int = Field(
        default=25 * 1024 * 1024,  # 25 MB
        description="Maximum file upload size in bytes"
    )

    # Rate Limiting & Auth
    max_failed_logins: int = Field(default=5)
    lockout_duration_minutes: int = Field(default=15)
    session_lifetime_days: int = Field(default=14)

    # Notifications & Alerts
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: str = "alerts@lifeledger.internal"

    class Config:
        env_prefix = "LIFELEDGER_"
        case_sensitive = False


# Global singleton instance
settings = LifeLedgerSettings()
