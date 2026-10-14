"""
OCR and Extracted Field Database Entities.
Tracks field keys, confidence ratings, normalized text, bounding boxes,
and human verification flags.
"""
from typing import Optional
from sqlalchemy import Boolean, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from lifeledger_models.base import Base, TimestampMixin, generate_uuid


class ExtractedField(Base, TimestampMixin):
    __tablename__ = "extracted_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    field_key: Mapped[str] = mapped_column(String(50), nullable=False)  # policy_number | total_amount | expiry_date | vendor_name | serial_number
    extracted_value: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    is_user_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bounding_box_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON {x, y, width, height}

    version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="extracted_fields")

    __table_args__ = (
        Index("idx_extracted_fields_key", "field_key"),
    )
