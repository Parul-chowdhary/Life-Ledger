"""
Asset, Warranty, and Claim Generation Service.
Calculates remaining warranty protection periods, straight-line depreciation,
and generates formal warranty claim dispute letters.
"""
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from lifeledger_models.entities.asset import Asset, MaintenanceLog
from lifeledger_repositories.asset_repository import AssetRepository


class AssetService:
    def __init__(self, session: Session):
        self.session = session
        self.asset_repo = AssetRepository(session)

    def calculate_warranty_status(self, asset: Asset, current_date: Optional[date] = None) -> Dict[str, Any]:
        """Calculates days remaining, status badge, and percentage of warranty elapsed."""
        today = current_date or date.today()
        if not asset.warranty_expiry_date:
            return {"status": "no_warranty", "days_remaining": 0, "badge": "secondary", "label": "No Warranty"}

        days_remaining = (asset.warranty_expiry_date - today).days

        if days_remaining < 0:
            return {
                "status": "expired",
                "days_remaining": days_remaining,
                "badge": "danger",
                "label": "Expired",
                "percent_elapsed": 100,
            }
        elif days_remaining <= 30:
            return {
                "status": "expiring_soon",
                "days_remaining": days_remaining,
                "badge": "warning",
                "label": f"Expiring in {days_remaining}d",
                "percent_elapsed": 90,
            }
        else:
            return {
                "status": "active",
                "days_remaining": days_remaining,
                "badge": "success",
                "label": f"Active ({days_remaining}d left)",
                "percent_elapsed": max(10, min(80, 100 - int(days_remaining / 10))),
            }

    def calculate_depreciation(self, asset: Asset, useful_life_years: int = 5) -> Dict[str, float]:
        """Calculates current book value using straight-line depreciation."""
        if not asset.purchase_price or not asset.purchase_date:
            return {"current_value": 0.0, "annual_depreciation": 0.0}

        annual_depreciation = asset.purchase_price / max(1, useful_life_years)
        years_held = (date.today() - asset.purchase_date).days / 365.25
        depreciated = min(asset.purchase_price, annual_depreciation * years_held)
        current_value = max(0.0, asset.purchase_price - depreciated)

        return {
            "original_price": asset.purchase_price,
            "current_value": round(current_value, 2),
            "annual_depreciation": round(annual_depreciation, 2),
        }

    def generate_warranty_claim_letter(
        self,
        asset_id: str,
        workspace_id: str,
        claimant_name: str,
        defect_description: str,
        desired_remedy: str = "Repair or Replacement under Limited Warranty",
    ) -> Dict[str, Any]:
        """Generates a formal, professional warranty claim letter template ready to send to vendor."""
        asset = self.asset_repo.get_by_id_scoped(asset_id, workspace_id)
        if not asset:
            raise ValueError("Asset not found")

        today_str = date.today().strftime("%B %d, %Y")
        purchase_date_str = asset.purchase_date.strftime("%B %d, %Y") if asset.purchase_date else "N/A"
        warranty_expiry_str = asset.warranty_expiry_date.strftime("%B %d, %Y") if asset.warranty_expiry_date else "Active"

        letter_content = f"""Date: {today_str}

To: Customer Support / Warranty Claims Department
Manufacturer: {asset.manufacturer or 'Manufacturer'}
Model: {asset.model_number or 'N/A'}
Serial Number (S/N): {asset.serial_number or 'N/A'}

From:
{claimant_name}
LifeLedger Registered Warranty Holder

SUBJECT: FORMAL WARRANTY SERVICE & REPAIR CLAIM — {asset.name}

Dear Customer Support Team,

I am writing to formally submit a warranty repair/replacement claim for my {asset.name} (Model: {asset.model_number or 'N/A'}, Serial Number: {asset.serial_number or 'N/A'}), purchased on {purchase_date_str}.

According to the manufacturer terms, this product is covered under limited warranty through {warranty_expiry_str}. The device is currently within its valid warranty protection period.

NATURE OF DEFECT / FAILURE:
{defect_description}

DEMANDED REMEDY:
Pursuant to the applicable consumer protection warranty provisions, I request {desired_remedy} at no additional cost. 

Enclosed with this notice is the original proof of purchase invoice and device identification details. Please provide an RMA (Return Merchandise Authorization) number and prepaid shipping instructions within five (5) business days.

Sincerely,

{claimant_name}
Enclosures: Proof of Purchase, Device Inspection Record
Generated via LifeLedger Intelligence Platform
"""
        return {
            "asset_name": asset.name,
            "manufacturer": asset.manufacturer,
            "serial_number": asset.serial_number,
            "letter_body": letter_content,
        }
