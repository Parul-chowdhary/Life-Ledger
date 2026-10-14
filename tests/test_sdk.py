"""
Unit Tests for LifeLedger Python SDK.
Tests SDK models validation, error handling, and client methods.
"""
from datetime import date, datetime
import pytest
from lifeledger_sdk.client import LifeLedgerClient, LifeLedgerSDKError
from lifeledger_sdk.models import (
    AssetRecord, DeadlineRecord, DocumentRecord, UserProfile,
    WarrantyClaimLetter, WarrantyStatusDTO
)


def test_sdk_model_validations():
    # User Profile model
    user = UserProfile(
        id="usr-123",
        email="test@example.com",
        full_name="Sarah",
        role="user",
        is_active=True,
    )
    assert user.email == "test@example.com"

    # Deadline Record model
    dl = DeadlineRecord(
        id="dl-99",
        workspace_id="ws-1",
        title="Insurance Renewal",
        due_date=date(2026, 10, 18),
        priority="high",
        renewal_cost=480.0,
    )
    assert dl.due_date.year == 2026
    assert dl.renewal_cost == 480.0

    # Warranty Status DTO model
    ws = WarrantyStatusDTO(
        status="active",
        days_remaining=45,
        badge="success",
        label="Active (45d left)",
    )
    assert ws.days_remaining == 45


def test_sdk_client_ping(client):
    sdk = LifeLedgerClient(base_url="http://127.0.0.1:5000")
    # Verify openapi spec fetch
    spec = sdk.get_openapi_spec()
    assert "openapi" in spec
    assert spec["info"]["title"] == "LifeLedger Intelligence Platform API"
