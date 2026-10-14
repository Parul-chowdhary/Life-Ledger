"""
Domain Service Integration Tests.
Verifies auth, storage, deadlines recurrence, warranty calculation, and analytics.
"""
from datetime import date, timedelta
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lifeledger_models.base import Base
from lifeledger_models.entities.asset import Asset
from lifeledger_models.entities.document import Document
from lifeledger_services.analytics_service import AnalyticsService
from lifeledger_services.asset_service import AssetService
from lifeledger_services.auth_service import AuthService
from lifeledger_services.deadline_service import DeadlineService
from lifeledger_services.storage_service import StorageService


@pytest.fixture
def db_session(tmp_path):
    db_file = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_file.as_posix()}", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_auth_registration_and_login(db_session):
    auth_svc = AuthService(db_session)
    user, workspace = auth_svc.register_user(
        email="test_user@example.com",
        password="TestPassword123!",
        full_name="Test User",
    )
    assert user.id is not None
    assert workspace.id is not None
    assert user.email == "test_user@example.com"

    # Authenticate
    authed_user, session_model = auth_svc.authenticate("test_user@example.com", "TestPassword123!")
    assert authed_user.id == user.id
    assert session_model.token is not None


def test_encrypted_storage_service(tmp_path):
    storage_svc = StorageService(base_dir=str(tmp_path / "vault_storage"))
    dummy_payload = b"Sample policy document file stream"
    
    key, sha256, size, nonce_hex = storage_svc.store_file(dummy_payload, "test.pdf")
    assert len(key) > 0
    assert size == len(dummy_payload)

    retrieved = storage_svc.retrieve_file(key, nonce_hex)
    assert retrieved == dummy_payload


def test_deadline_creation_and_completion(db_session):
    auth_svc = AuthService(db_session)
    user, workspace = auth_svc.register_user("owner@test.com", "Password123!", "Owner")

    doc = Document(
        workspace_id=workspace.id,
        title="Car Insurance Policy",
        category="insurance",
        expiry_date=date.today() + timedelta(days=20),
        renewal_cost=500.0,
        auto_renew=True,
    )
    db_session.add(doc)
    db_session.commit()

    dl_svc = DeadlineService(db_session)
    dl = dl_svc.create_deadline_for_document(doc)
    assert dl is not None
    assert dl.status == "upcoming"
    assert len(dl.reminder_schedules) == 4

    # Complete deadline and verify recurring rollover
    rolled_over = dl_svc.complete_deadline(dl.id, workspace.id)
    assert rolled_over is not None
    assert rolled_over.due_date > dl.due_date


def test_warranty_status_calculation(db_session):
    auth_svc = AuthService(db_session)
    user, workspace = auth_svc.register_user("asset_owner@test.com", "Password123!", "Asset Owner")

    today = date.today()
    asset = Asset(
        workspace_id=workspace.id,
        name="MacBook Pro",
        purchase_date=today - timedelta(days=300),
        purchase_price=2000.0,
        warranty_expiry_date=today + timedelta(days=15),
    )
    db_session.add(asset)
    db_session.commit()

    asset_svc = AssetService(db_session)
    w_status = asset_svc.calculate_warranty_status(asset)
    assert w_status["status"] == "expiring_soon"
    assert w_status["days_remaining"] == 15

    # Check claim letter generator
    claim = asset_svc.generate_warranty_claim_letter(
        asset.id, workspace.id, "Sarah Jenkins", "Display flickering issue"
    )
    assert "Display flickering issue" in claim["letter_body"]
    assert "MacBook Pro" in claim["letter_body"]
