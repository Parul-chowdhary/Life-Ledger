"""
Document, Version, and Tagging Entities.
Implements metadata catalogs, immutable version history, file deduplication keys,
emergency ICE flags, and custom tag assignments.
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger, Boolean, Column, Date, DateTime, ForeignKey,
    Index, Integer, String, Table, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from lifeledger_models.base import Base, TimestampMixin, generate_uuid

# Document Tags Many-to-Many Association
document_tags_association = Table(
    "document_tags_association",
    Base.metadata,
    Column("document_id", String(36), ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String(36), ForeignKey("document_tags.id", ondelete="CASCADE"), primary_key=True),
)


class DocumentTag(Base):
    __tablename__ = "document_tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#4f46e5", nullable=False)

    documents: Mapped[List["Document"]] = relationship(
        "Document", secondary=document_tags_association, back_populates="tags"
    )

    __table_args__ = (
        UniqueConstraint("workspace_id", "name", name="uq_workspace_tag_name"),
    )


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: identity, insurance, warranty, bill, vehicle, property, education, legal, tax, other
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)  # pending_ocr | active | archived
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_ice_document: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    renewal_cost: Mapped[Optional[float]] = mapped_column(default=0.0, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(
        "DocumentVersion", back_populates="document", cascade="all, delete-orphan", order_by="desc(DocumentVersion.version_number)"
    )
    tags: Mapped[List["DocumentTag"]] = relationship(
        "DocumentTag", secondary=document_tags_association, back_populates="documents"
    )
    deadlines: Mapped[List["Deadline"]] = relationship(
        "Deadline", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_docs_workspace_category", "workspace_id", "category"),
        Index("idx_docs_expiry", "expiry_date"),
        Index("idx_docs_status", "status"),
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    encryption_iv: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    extracted_fields: Mapped[List["ExtractedField"]] = relationship(
        "ExtractedField", back_populates="version", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("document_id", "version_number", name="uq_doc_version_num"),
    )
