"""
LifeLedger Official Python Client SDK.
Provides typed access to documents, deadlines, warranties, and analytics.
"""
from lifeledger_sdk.client import LifeLedgerClient, LifeLedgerSDKError
from lifeledger_sdk.models import (
    AssetRecord,
    CashFlowBucket,
    DashboardMetrics,
    DeadlineRecord,
    DocumentRecord,
    DocumentVersionDTO,
    UserProfile,
    WarrantyClaimLetter,
    WarrantyStatusDTO,
    WorkspaceSummary,
)

__version__ = "1.0.0"

__all__ = [
    "LifeLedgerClient",
    "LifeLedgerSDKError",
    "UserProfile",
    "WorkspaceSummary",
    "DocumentRecord",
    "DocumentVersionDTO",
    "DeadlineRecord",
    "AssetRecord",
    "WarrantyStatusDTO",
    "WarrantyClaimLetter",
    "DashboardMetrics",
    "CashFlowBucket",
]
