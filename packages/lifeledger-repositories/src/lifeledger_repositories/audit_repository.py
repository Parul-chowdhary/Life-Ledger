"""
Audit Log and Security Event Repository.
Provides append-only audit trail logging and tamper-evident event queries.
"""
import json
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from lifeledger_models.entities.audit import AuditLog, SharedLink
from lifeledger_repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, session: Session):
        super().__init__(session, AuditLog)

    def log_event(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            workspace_id=workspace_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=json.dumps(metadata or {}),
        )
        self.session.add(log)
        return log

    def list_recent(self, workspace_id: Optional[str] = None, limit: int = 50) -> List[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.created_at.desc())
        if workspace_id:
            stmt = stmt.where(AuditLog.workspace_id == workspace_id)
        return list(self.session.scalars(stmt.limit(limit)).all())


class SharedLinkRepository(BaseRepository[SharedLink]):
    def __init__(self, session: Session):
        super().__init__(session, SharedLink)

    def get_by_token(self, token: str) -> Optional[SharedLink]:
        stmt = select(SharedLink).where(SharedLink.token == token)
        return self.session.scalars(stmt).first()
