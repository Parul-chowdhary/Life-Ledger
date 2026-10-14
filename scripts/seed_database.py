#!/usr/bin/env python3
"""
LifeLedger Comprehensive Database Seeder.
Creates demo user, administrative auditor, and realistic household lifecycle records
including auto insurance, appliance warranties, utility bills, passports, and deadlines.
"""
from datetime import date, timedelta
import sys
from pathlib import Path

# Fix Windows console encoding for Unicode/emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-core" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-models" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-repositories" / "src"))
sys.path.insert(0, str(ROOT_DIR / "packages" / "lifeledger-services" / "src"))

from lifeledger_core.config import settings
from lifeledger_models.base import Base
from lifeledger_models.entities.asset import Asset
from lifeledger_models.entities.document import Document, DocumentVersion
from lifeledger_models.entities.user import User
from lifeledger_models.entities.workspace import Workspace, WorkspaceMembership
from lifeledger_services.auth_service import AuthService
from lifeledger_services.deadline_service import DeadlineService
from lifeledger_services.storage_service import StorageService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def seed():
    # Ensure storage and instance directories exist first
    (ROOT_DIR / "instance").mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "var" / "storage").mkdir(parents=True, exist_ok=True)

    print("[*] Initializing LifeLedger Database Seeder...")

    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    auth_svc = AuthService(session)
    storage_svc = StorageService()
    dl_svc = DeadlineService(session)

    # 1. Check or Create Demo User
    demo_email = "sarah@example.com"
    user = session.query(User).filter_by(email=demo_email).first()
    if not user:
        user, workspace = auth_svc.register_user(
            email=demo_email,
            password="Password123!",
            full_name="Sarah Jenkins",
            role="user"
        )
        print(f"  [+] Created Demo User: {demo_email} (Password: Password123!)")
    else:
        workspace = auth_svc.get_user_default_workspace(user.id)
        print(f"  [i] Demo User {demo_email} already exists.")

    # 2. Check or Create Admin User
    admin_email = "admin@lifeledger.internal"
    admin_user = session.query(User).filter_by(email=admin_email).first()
    if not admin_user:
        admin_user, _ = auth_svc.register_user(
            email=admin_email,
            password="AdminSecret2026!",
            full_name="System Auditor",
            role="admin"
        )
        print(f"  [+] Created Admin User: {admin_email} (Password: AdminSecret2026!)")

    # 3. Populate Sample Lifecycle Documents
    today = date.today()

    sample_docs = [
        {
            "title": "Geico Automobile Comprehensive Insurance",
            "category": "insurance",
            "issuer": "Geico Casualty Co.",
            "issue_date": today - timedelta(days=360),
            "expiry_date": today + timedelta(days=4),  # Due in 4 days!
            "cost": 480.00,
            "auto_renew": False,
            "ice": False,
            "notes": "Policy # POL-AUTO-892144. $500 Comprehensive / Collision Deductible. 24/7 Roadside Assistance: 1-800-841-3000.",
            "file_name": "geico_auto_policy_2026.pdf",
            "dummy_content": b"%PDF-1.4 Mock Geico Policy POL-AUTO-892144 Expiry: Oct 18, 2026 Total: $480.00",
        },
        {
            "title": "MacBook Pro 16\" M3 AppleCare+ Warranty",
            "category": "warranty",
            "issuer": "Apple Inc.",
            "issue_date": today - timedelta(days=700),
            "expiry_date": today + timedelta(days=12),  # Due in 12 days!
            "cost": 0.00,
            "auto_renew": False,
            "ice": False,
            "notes": "Serial # C02G901XMD6R. AppleCare+ Agreement # AC-991823. Covers accidental damage & battery service.",
            "file_name": "applecare_proof_of_coverage.pdf",
            "dummy_content": b"%PDF-1.4 AppleCare Agreement AC-991823 Serial: C02G901XMD6R Valid through Oct 26, 2026",
        },
        {
            "title": "United States Passport — Sarah Jenkins",
            "category": "identity",
            "issuer": "U.S. Department of State",
            "issue_date": today - timedelta(days=1800),
            "expiry_date": today + timedelta(days=1700),
            "cost": 130.00,
            "auto_renew": False,
            "ice": True,  # ICE emergency record
            "notes": "Passport Book # P88219034. Emergency Contact: David Jenkins (+1-555-0192). In Case of Emergency Flag Enabled.",
            "file_name": "us_passport_sarah_jenkins.pdf",
            "dummy_content": b"%PDF-1.4 US Passport P88219034 Sarah Jenkins",
        },
        {
            "title": "City Water & Sewer Utility Contract",
            "category": "bill",
            "issuer": "Department of Water & Power",
            "issue_date": today - timedelta(days=25),
            "expiry_date": today + timedelta(days=19),
            "cost": 84.50,
            "auto_renew": True,
            "ice": False,
            "notes": "Account # UTIL-9901-WATER. Auto-debit from checking account scheduled 2 days prior to due date.",
            "file_name": "water_utility_invoice_oct2026.pdf",
            "dummy_content": b"%PDF-1.4 Utility Bill UTIL-9901-WATER Total: $84.50 Due in 19 days",
        },
        {
            "title": "Sony BRAVIA 75\" OLED Extended Warranty",
            "category": "warranty",
            "issuer": "Sony Electronics",
            "issue_date": today - timedelta(days=180),
            "expiry_date": today + timedelta(days=180),
            "cost": 0.00,
            "auto_renew": False,
            "ice": False,
            "notes": "Serial # SN-SONY-778219. Best Buy Geek Squad Protection Agreement # GS-88912.",
            "file_name": "sony_bravia_warranty_contract.pdf",
            "dummy_content": b"%PDF-1.4 Sony Bravia Warranty SN-SONY-778219",
        },
        {
            "title": "Residential Property Title & Deed",
            "category": "property",
            "issuer": "County Registrar of Deeds",
            "issue_date": today - timedelta(days=1200),
            "expiry_date": None,
            "cost": 0.00,
            "auto_renew": False,
            "ice": True,
            "notes": "Parcel # APN-442-990-12. Title Insurance policy underwritten by First American Title.",
            "file_name": "residential_property_deed_signed.pdf",
            "dummy_content": b"%PDF-1.4 Property Deed Parcel APN-442-990-12",
        },
    ]

    for item in sample_docs:
        existing_doc = session.query(Document).filter_by(workspace_id=workspace.id, title=item["title"]).first()
        if not existing_doc:
            # Store encrypted dummy file
            storage_key, sha256_hash, file_size, nonce_hex = storage_svc.store_file(
                item["dummy_content"], item["file_name"]
            )

            doc = Document(
                workspace_id=workspace.id,
                created_by=user.id,
                title=item["title"],
                category=item["category"],
                issue_date=item["issue_date"],
                expiry_date=item["expiry_date"],
                issuing_authority=item["issuer"],
                status="active",
                is_ice_document=item["ice"],
                renewal_cost=item["cost"],
                auto_renew=item["auto_renew"],
                notes=item["notes"],
            )
            session.add(doc)
            session.flush()

            ver = DocumentVersion(
                document_id=doc.id,
                version_number=1,
                storage_key=storage_key,
                file_name=item["file_name"],
                mime_type="application/pdf",
                file_size_bytes=file_size,
                sha256_hash=sha256_hash,
                encryption_iv=nonce_hex,
            )
            session.add(ver)

            if doc.expiry_date:
                dl_svc.create_deadline_for_document(doc)

            print(f"  [+] Vaulted Document: {doc.title} ({doc.category})")

    # 4. Catalog Assets & Hardware
    sample_assets = [
        {
            "name": "Apple MacBook Pro 16\" (M3 Max)",
            "category": "electronics",
            "manufacturer": "Apple Inc.",
            "model_number": "A2991",
            "serial_number": "C02G901XMD6R",
            "purchase_date": today - timedelta(days=700),
            "purchase_price": 3499.00,
            "warranty_months": 36,
            "warranty_expiry_date": today + timedelta(days=12),
            "support_phone": "1-800-275-2273",
        },
        {
            "name": "Sony BRAVIA XR 75\" 4K OLED TV",
            "category": "electronics",
            "manufacturer": "Sony",
            "model_number": "XR-75A80L",
            "serial_number": "SN-SONY-778219",
            "purchase_date": today - timedelta(days=180),
            "purchase_price": 2499.00,
            "warranty_months": 24,
            "warranty_expiry_date": today + timedelta(days=180),
            "support_phone": "1-800-222-7669",
        },
        {
            "name": "Bosch 800 Series Dishwasher",
            "category": "appliance",
            "manufacturer": "Bosch",
            "model_number": "SHPM88Z75N",
            "serial_number": "BSH-881902",
            "purchase_date": today - timedelta(days=320),
            "purchase_price": 1299.00,
            "warranty_months": 12,
            "warranty_expiry_date": today + timedelta(days=45),
            "support_phone": "1-800-944-2904",
        },
        {
            "name": "Tesla Model Y Long Range",
            "category": "vehicle",
            "manufacturer": "Tesla",
            "model_number": "Model Y 2024",
            "serial_number": "5YJYGDEE8PF19283",
            "purchase_date": today - timedelta(days=365),
            "purchase_price": 48990.00,
            "warranty_months": 48,
            "warranty_expiry_date": today + timedelta(days=730),
            "support_phone": "1-888-518-3752",
        },
    ]

    for a_data in sample_assets:
        existing_asset = session.query(Asset).filter_by(workspace_id=workspace.id, name=a_data["name"]).first()
        if not existing_asset:
            asset = Asset(
                workspace_id=workspace.id,
                name=a_data["name"],
                category=a_data["category"],
                manufacturer=a_data["manufacturer"],
                model_number=a_data["model_number"],
                serial_number=a_data["serial_number"],
                purchase_date=a_data["purchase_date"],
                purchase_price=a_data["purchase_price"],
                warranty_months=a_data["warranty_months"],
                warranty_expiry_date=a_data["warranty_expiry_date"],
                support_phone=a_data["support_phone"],
            )
            session.add(asset)
            print(f"  [+] Cataloged Asset: {asset.name} (S/N: {asset.serial_number})")

    session.commit()
    print("[*] Seeding successfully completed!")


if __name__ == "__main__":
    seed()
