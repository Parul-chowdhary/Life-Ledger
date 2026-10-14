"""
LifeLedger Python SDK Typed Data Models.
Defines strongly-typed request and response structures for all platform entities.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    mfa_enabled: bool = False
    created_at: Optional[datetime] = None


class WorkspaceSummary(BaseModel):
    id: str
    name: str
    owner_id: str
    storage_quota_bytes: int
    current_storage_bytes: int


class DocumentVersionDTO(BaseModel):
    id: str
    version_number: int
    file_name: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    created_at: datetime


class DocumentRecord(BaseModel):
    id: str
    workspace_id: str
    title: str
    category: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = None
    status: str
    is_ice_document: bool = False
    renewal_cost: Optional[float] = 0.0
    auto_renew: bool = False
    notes: Optional[str] = None
    versions: List[DocumentVersionDTO] = Field(default_factory=list)


class DeadlineRecord(BaseModel):
    id: str
    workspace_id: str
    document_id: Optional[str] = None
    title: str
    due_date: date
    recurrence_rule: Optional[str] = None
    priority: str = "medium"
    status: str = "upcoming"
    renewal_cost: Optional[float] = 0.0
    notes: Optional[str] = None


class AssetRecord(BaseModel):
    id: str
    workspace_id: str
    name: str
    category: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = 0.0
    warranty_months: int = 12
    warranty_expiry_date: Optional[date] = None
    support_phone: Optional[str] = None


class WarrantyStatusDTO(BaseModel):
    status: str  # active | expiring_soon | expired | no_warranty
    days_remaining: int
    badge: str
    label: str
    percent_elapsed: Optional[int] = 0


class WarrantyClaimLetter(BaseModel):
    asset_name: str
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    letter_body: str


class DashboardMetrics(BaseModel):
    total_documents: int
    due_30d_cost: float
    urgent_count: int
    overdue_count: int
    active_warranties: int
    total_warranty_value: float
    health_score: int


class CashFlowBucket(BaseModel):
    month: str
    key: str
    amount: float
