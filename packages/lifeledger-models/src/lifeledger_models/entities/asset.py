"""
Asset, Warranty, and Maintenance Log Database Entities.
Tracks household appliances, electronics, vehicles, serial numbers,
purchase invoices, warranty status, and service expenses.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy import Date, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from lifeledger_models.base import Base, TimestampMixin, generate_uuid


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), default="electronics", nullable=False)  # electronics | appliance | vehicle | home | tools
    manufacturer: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    purchase_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    warranty_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    warranty_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    support_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    support_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invoice_document_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="assets")
    maintenance_logs: Mapped[List["MaintenanceLog"]] = relationship(
        "MaintenanceLog", back_populates="asset", cascade="all, delete-orphan", order_by="desc(MaintenanceLog.service_date)"
    )

    __table_args__ = (
        Index("idx_assets_workspace_category", "workspace_id", "category"),
    )


class MaintenanceLog(Base, TimestampMixin):
    __tablename__ = "maintenance_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    asset_id: Mapped[str] = mapped_column(String(36), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_type: Mapped[str] = mapped_column(String(100), nullable=False)  # routine | repair | inspection | upgrade
    provider_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    receipt_document_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

    asset: Mapped["Asset"] = relationship("Asset", back_populates="maintenance_logs")
