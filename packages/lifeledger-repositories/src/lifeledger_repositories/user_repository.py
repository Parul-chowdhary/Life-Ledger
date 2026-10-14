"""
User and Session Repository.
Handles user retrieval by email, session lookup and revocation, and lockouts.
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from lifeledger_models.entities.user import SessionModel, User
from lifeledger_repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.strip().lower())
        return self.session.scalars(stmt).first()

    def get_active_session(self, token: str) -> Optional[SessionModel]:
        now = datetime.now(timezone.utc)
        stmt = select(SessionModel).where(
            SessionModel.token == token,
            SessionModel.expires_at > now
        )
        return self.session.scalars(stmt).first()

    def create_session(self, user_id: str, token: str, expires_at: datetime, ip: Optional[str] = None, ua: Optional[str] = None) -> SessionModel:
        sess = SessionModel(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            ip_address=ip,
            user_agent=ua,
        )
        self.session.add(sess)
        return sess

    def revoke_session(self, token: str) -> None:
        stmt = delete(SessionModel).where(SessionModel.token == token)
        self.session.execute(stmt)

    def revoke_all_user_sessions(self, user_id: str) -> None:
        stmt = delete(SessionModel).where(SessionModel.user_id == user_id)
        self.session.execute(stmt)
