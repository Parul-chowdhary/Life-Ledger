"""
Administrative Governance & Telemetry Service.
Provides system health checks, user status controls, storage quota monitoring,
and tamper-evident audit trail querying.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from lifeledger_models.entities.audit import AuditLog
from lifeledger_models.entities.document import Document
from lifeledger_models.entities.user import User
from lifeledger_models.entities.workspace import Workspace
from lifeledger_repositories.audit_repository import AuditRepository
from lifeledger_repositories.user_repository import UserRepository


class AdminService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditRepository(session)

    def get_system_health(self) -> Dict[str, Any]:
        """Collects operational metrics for administrative dashboard."""
        total_users = self.session.scalar(select(func.count(User.id))) or 0
        active_users = self.session.scalar(select(func.count(User.id)).where(User.is_active == True)) or 0
        total_docs = self.session.scalar(select(func.count(Document.id))) or 0
        total_workspaces = self.session.scalar(select(func.count(Workspace.id))) or 0

        # Calculate total storage across workspaces
        storage_sum = self.session.scalar(select(func.sum(Workspace.current_storage_bytes))) or 0

        return {
            "status": "healthy",
            "database": "connected",
            "total_users": total_users,
            "active_users": active_users,
            "total_documents": total_docs,
            "total_workspaces": total_workspaces,
            "storage_used_bytes": storage_sum,
            "storage_used_formatted": f"{storage_sum / (1024 * 1024):,.2f} MB",
        }

    def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def set_user_status(self, user_id: str, is_active: bool, actor_user_id: str) -> Optional[User]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        user.is_active = is_active
        self.audit_repo.log_event(
            action="admin.user_status_changed",
            resource_type="user",
            resource_id=user_id,
            user_id=actor_user_id,
            metadata={"new_status": is_active},
        )
        self.session.commit()
        return user

    def list_audit_trail(self, limit: int = 50) -> List[AuditLog]:
        return self.audit_repo.list_recent(limit=limit)
