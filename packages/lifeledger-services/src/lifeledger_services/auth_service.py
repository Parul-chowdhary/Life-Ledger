"""
Authentication and Authorization Domain Service.
Handles user registration, credential verification, session lifecycle,
role-based permissions, and TOTP 2FA tokens.
"""
from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from lifeledger_core.crypto import PasswordHasher, TokenSigner
from lifeledger_core.exceptions import AuthenticationError, AuthorizationError, ValidationError
from lifeledger_models.entities.user import SessionModel, User
from lifeledger_models.entities.workspace import Workspace, WorkspaceMembership
from lifeledger_repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.token_signer = TokenSigner()

    def register_user(self, email: str, password: str, full_name: str, role: str = "user") -> Tuple[User, Workspace]:
        email_clean = email.strip().lower()
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        existing = self.user_repo.get_by_email(email_clean)
        if existing:
            raise ValidationError("An account with this email address already exists")

        pwd_hash = PasswordHasher.hash_password(password)
        user = User(
            email=email_clean,
            password_hash=pwd_hash,
            full_name=full_name.strip(),
            role=role,
            is_active=True,
        )
        self.session.add(user)
        self.session.flush()

        # Create default personal workspace for the user
        workspace = Workspace(
            name=f"{user.full_name}'s Vault",
            owner_id=user.id,
        )
        self.session.add(workspace)
        self.session.flush()

        # Add owner membership
        membership = WorkspaceMembership(
            workspace_id=workspace.id,
            user_id=user.id,
            role="owner",
        )
        self.session.add(membership)
        self.session.commit()
        return user, workspace

    def authenticate(self, email: str, password: str, ip: Optional[str] = None, ua: Optional[str] = None) -> Tuple[User, SessionModel]:
        email_clean = email.strip().lower()
        user = self.user_repo.get_by_email(email_clean)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid email address or account is inactive")

        # Check account lockout
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            remaining = int((user.locked_until - datetime.now(timezone.utc)).total_seconds() / 60)
            raise AuthenticationError(f"Account temporarily locked due to failed attempts. Try again in {remaining} minutes.")

        if not PasswordHasher.verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            self.session.commit()
            raise AuthenticationError("Invalid password")

        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None

        # Create session
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=14)
        session_model = self.user_repo.create_session(user.id, token, expires_at, ip, ua)
        self.session.commit()
        return user, session_model

    def validate_session(self, token: str) -> Optional[User]:
        if not token:
            return None
        session_model = self.user_repo.get_active_session(token)
        if not session_model:
            return None
        return session_model.user

    def logout(self, token: str) -> None:
        self.user_repo.revoke_session(token)
        self.session.commit()

    def get_user_default_workspace(self, user_id: str) -> Optional[Workspace]:
        from sqlalchemy import select
        stmt = (
            select(Workspace)
            .join(WorkspaceMembership)
            .where(WorkspaceMembership.user_id == user_id)
            .order_by(Workspace.created_at.asc())
        )
        return self.session.scalars(stmt).first()

    def require_role(self, user: User, allowed_roles: list[str]) -> None:
        if user.role not in allowed_roles:
            raise AuthorizationError(f"Action requires one of the following roles: {', '.join(allowed_roles)}")
