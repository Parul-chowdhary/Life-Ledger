"""
Deadline and Notification Schedule Database Entities.
Implements temporal intelligence, RFC 5545 recurrence rules, priority tiers,
and multi-stage notification dispatch tracking.
"""
from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from lifeledger_models.base import Base, TimestampMixin, generate_uuid


class Deadline(Base, TimestampMixin):
    __tablename__ = "deadlines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # RFC 5545 e.g. FREQ=YEARLY;INTERVAL=1
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low | medium | high | urgent
    status: Mapped[str] = mapped_column(String(30), default="upcoming", nullable=False, index=True)  # upcoming | overdue | completed | dismissed
    renewal_cost: Mapped[Optional[float]] = mapped_column(default=0.0, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_evaluated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="deadlines")
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="deadlines")
    reminder_schedules: Mapped[List["ReminderSchedule"]] = relationship(
        "ReminderSchedule", back_populates="deadline", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_deadlines_workspace_due", "workspace_id", "due_date"),
        Index("idx_deadlines_status_due", "status", "due_date"),
    )


class ReminderSchedule(Base, TimestampMixin):
    __tablename__ = "reminder_schedules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    deadline_id: Mapped[str] = mapped_column(String(36), ForeignKey("deadlines.id", ondelete="CASCADE"), nullable=False, index=True)
    days_before: Mapped[int] = mapped_column(Integer, nullable=False)  # 60, 30, 14, 7, 1, 0
    channel: Mapped[str] = mapped_column(String(30), default="in_app", nullable=False)  # in_app | email | webhook
    is_dispatched: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    deadline: Mapped["Deadline"] = relationship("Deadline", back_populates="reminder_schedules")
    notification_attempts: Mapped[List["NotificationAttempt"]] = relationship(
        "NotificationAttempt", back_populates="schedule", cascade="all, delete-orphan"
    )


class NotificationAttempt(Base, TimestampMixin):
    __tablename__ = "notification_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    schedule_id: Mapped[str] = mapped_column(String(36), ForeignKey("reminder_schedules.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)  # success | failed | retry
    response_payload: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    schedule: Mapped["ReminderSchedule"] = relationship("ReminderSchedule", back_populates="notification_attempts")
