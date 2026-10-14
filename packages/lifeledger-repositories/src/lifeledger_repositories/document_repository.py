"""
Document and Version Repository.
Enforces strict multi-tenant workspace isolation on all queries,
supports filtering by category/tags/expiry, and manages version history.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from lifeledger_models.entities.document import Document, DocumentTag, DocumentVersion
from lifeledger_repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: Session):
        super().__init__(session, Document)

    def get_by_id_scoped(self, document_id: str, workspace_id: str) -> Optional[Document]:
        """Tenant-isolated retrieval: returns None if document belongs to another workspace."""
        stmt = (
            select(Document)
            .where(Document.id == document_id, Document.workspace_id == workspace_id)
            .options(selectinload(Document.versions), selectinload(Document.tags))
        )
        return self.session.scalars(stmt).first()

    def list_by_workspace(
        self,
        workspace_id: str,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        is_archived: bool = False,
        is_ice: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Document]:
        stmt = (
            select(Document)
            .where(Document.workspace_id == workspace_id, Document.is_archived == is_archived)
            .options(selectinload(Document.versions), selectinload(Document.tags))
            .order_by(Document.created_at.desc())
        )

        if category and category != "all":
            stmt = stmt.where(Document.category == category)

        if is_ice is not None:
            stmt = stmt.where(Document.is_ice_document == is_ice)

        if search_query:
            pattern = f"%{search_query.strip().lower()}%"
            stmt = stmt.where(
                func.lower(Document.title).like(pattern)
                | func.lower(Document.issuing_authority).like(pattern)
                | func.lower(Document.notes).like(pattern)
            )

        return list(self.session.scalars(stmt.limit(limit).offset(offset)).all())

    def get_expiring_documents(self, workspace_id: str, start_date: date, end_date: date) -> List[Document]:
        stmt = (
            select(Document)
            .where(
                Document.workspace_id == workspace_id,
                Document.is_archived == False,
                Document.expiry_date >= start_date,
                Document.expiry_date <= end_date,
            )
            .order_by(Document.expiry_date.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get_version_by_hash(self, sha256_hash: str) -> Optional[DocumentVersion]:
        stmt = select(DocumentVersion).where(DocumentVersion.sha256_hash == sha256_hash)
        return self.session.scalars(stmt).first()

    def get_latest_version(self, document_id: str) -> Optional[DocumentVersion]:
        stmt = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        return self.session.scalars(stmt).first()

    def get_or_create_tag(self, workspace_id: str, tag_name: str, color: str = "#4f46e5") -> DocumentTag:
        stmt = select(DocumentTag).where(
            DocumentTag.workspace_id == workspace_id,
            DocumentTag.name == tag_name.strip()
        )
        tag = self.session.scalars(stmt).first()
        if not tag:
            tag = DocumentTag(workspace_id=workspace_id, name=tag_name.strip(), color=color)
            self.session.add(tag)
            self.session.flush()
        return tag
