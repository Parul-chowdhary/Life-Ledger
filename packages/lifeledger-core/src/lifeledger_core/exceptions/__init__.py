"""
LifeLedger Unified Exception Hierarchy.
Provides consistent error codes, HTTP status mapping, and sanitized serialization.
"""
from typing import Any, Dict, Optional


class LifeLedgerException(Exception):
    """Base exception for all LifeLedger domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class AuthenticationError(LifeLedgerException):
    """Raised when authentication credentials fail or are invalid."""

    def __init__(self, message: str = "Invalid authentication credentials", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="AUTHENTICATION_FAILED", status_code=401, details=details)


class AuthorizationError(LifeLedgerException):
    """Raised when an authenticated actor lacks permission for an operation."""

    def __init__(self, message: str = "You do not have permission to access this resource", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="FORBIDDEN", status_code=403, details=details)


class ResourceNotFoundError(LifeLedgerException):
    """Raised when a requested resource does not exist or is not visible to tenant."""

    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            f"{resource} with identifier '{identifier}' was not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": str(identifier)},
        )


class ValidationError(LifeLedgerException):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_FAILED", status_code=400, details=details)


class StorageQuotaExceededError(LifeLedgerException):
    """Raised when a workspace exceeds its maximum allocated byte limit."""

    def __init__(self, current_bytes: int, quota_bytes: int):
        super().__init__(
            f"Storage quota exceeded: {current_bytes} / {quota_bytes} bytes used",
            code="STORAGE_QUOTA_EXCEEDED",
            status_code=402,
            details={"current_bytes": current_bytes, "quota_bytes": quota_bytes},
        )


class CryptographicError(LifeLedgerException):
    """Raised upon encryption, decryption, or signature verification failure."""

    def __init__(self, message: str = "Cryptographic integrity check failed"):
        super().__init__(message, code="CRYPTO_FAILURE", status_code=500)


class OCRProcessingError(LifeLedgerException):
    """Raised when OCR parsing fails unrecoverably."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="OCR_PROCESSING_FAILED", status_code=422, details=details)
