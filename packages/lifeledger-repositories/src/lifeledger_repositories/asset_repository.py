"""
Asset, Warranty, and Maintenance Log Repository.
Enforces workspace boundaries and provides warranty status queries.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from lifeledger_models.entities.asset import Asset, MaintenanceLog
from lifeledger_repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    def __init__(self, session: Session):
        super().__init__(session, Asset)

    def get_by_id_scoped(self, asset_id: str, workspace_id: str) -> Optional[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.id == asset_id, Asset.workspace_id == workspace_id)
            .options(selectinload(Asset.maintenance_logs))
        )
        return self.session.scalars(stmt).first()

    def list_by_workspace(self, workspace_id: str, category: Optional[str] = None) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(Asset.workspace_id == workspace_id)
            .options(selectinload(Asset.maintenance_logs))
            .order_by(Asset.created_at.desc())
        )
        if category and category != "all":
            stmt = stmt.where(Asset.category == category)
        return list(self.session.scalars(stmt).all())

    def get_expiring_warranties(self, workspace_id: str, start_date: date, end_date: date) -> List[Asset]:
        stmt = (
            select(Asset)
            .where(
                Asset.workspace_id == workspace_id,
                Asset.warranty_expiry_date >= start_date,
                Asset.warranty_expiry_date <= end_date,
            )
            .order_by(Asset.warranty_expiry_date.asc())
        )
        return list(self.session.scalars(stmt).all())

    def add_maintenance_log(self, log: MaintenanceLog) -> MaintenanceLog:
        self.session.add(log)
        return log
