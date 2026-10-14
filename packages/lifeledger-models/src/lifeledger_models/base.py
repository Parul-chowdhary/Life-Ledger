"""
LifeLedger Base Declarative Infrastructure.
Provides SQLAlchemy 2.0 declarative base, UUID generation,
and standard timestamp mixins.
"""
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Base declarative class for all LifeLedger ORM models."""

    def to_dict(self) -> dict[str, Any]:
        """Generic dictionary representation."""
        result = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, datetime):
                result[c.name] = val.isoformat()
            else:
                result[c.name] = val
        return result


class TimestampMixin:
    """Provides created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
