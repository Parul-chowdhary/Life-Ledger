"""
Deadline and Notification Schedule Repository.
Queries upcoming, overdue, and completed obligations with timezone awareness.
"""
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from lifeledger_models.entities.deadline import Deadline, ReminderSchedule
from lifeledger_repositories.base import BaseRepository


class DeadlineRepository(BaseRepository[Deadline]):
    def __init__(self, session: Session):
        super().__init__(session, Deadline)

    def get_by_id_scoped(self, deadline_id: str, workspace_id: str) -> Optional[Deadline]:
        stmt = (
            select(Deadline)
            .where(Deadline.id == deadline_id, Deadline.workspace_id == workspace_id)
            .options(selectinload(Deadline.reminder_schedules))
        )
        return self.session.scalars(stmt).first()

    def list_by_workspace(
        self,
        workspace_id: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Deadline]:
        stmt = (
            select(Deadline)
            .where(Deadline.workspace_id == workspace_id)
            .options(selectinload(Deadline.reminder_schedules))
            .order_by(Deadline.due_date.asc())
        )
        if status and status != "all":
            stmt = stmt.where(Deadline.status == status)
        return list(self.session.scalars(stmt.limit(limit).offset(offset)).all())

    def get_upcoming_or_overdue(self, workspace_id: str, threshold_date: date) -> List[Deadline]:
        """Fetches all active obligations due on or before threshold_date."""
        stmt = (
            select(Deadline)
            .where(
                Deadline.workspace_id == workspace_id,
                Deadline.status.in_(["upcoming", "overdue"]),
                Deadline.due_date <= threshold_date,
            )
            .order_by(Deadline.due_date.asc())
        )
        return list(self.session.scalars(stmt).all())

    def get_active_schedules_for_eval(self, eval_date: date) -> List[ReminderSchedule]:
        stmt = (
            select(ReminderSchedule)
            .join(Deadline)
            .where(
                ReminderSchedule.is_dispatched == False,
                Deadline.status == "upcoming",
            )
            .options(selectinload(ReminderSchedule.deadline))
        )
        return list(self.session.scalars(stmt).all())
