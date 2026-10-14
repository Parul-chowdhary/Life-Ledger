"""
Base Repository & Unit of Work Infrastructure.
Provides database session lifecycle management, generic CRUD primitives,
and transactional context managers.
"""
from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session
from lifeledger_models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic base repository providing common query and mutation operations."""

    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    def get_by_id(self, id_: str) -> Optional[T]:
        return self.session.get(self.model_class, id_)

    def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        stmt = select(self.model_class).limit(limit).offset(offset)
        return list(self.session.scalars(stmt).all())

    def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.session.delete(entity)

    def count(self) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model_class)
        return self.session.scalar(stmt) or 0


class UnitOfWork:
    """Manages transactional boundaries across multiple repositories."""

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = self.session_factory()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()
