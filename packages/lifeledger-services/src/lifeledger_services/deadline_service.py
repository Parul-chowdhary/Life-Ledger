"""
Deadline and Temporal Intelligence Engine.
Implements RFC 5545 recurrence rule processing, deadline state machines,
automatic deadline synthesis from document expiration dates, and iCalendar feed export.
"""
from datetime import date, datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from lifeledger_models.entities.deadline import Deadline, ReminderSchedule
from lifeledger_models.entities.document import Document
from lifeledger_repositories.deadline_repository import DeadlineRepository


class DeadlineService:
    def __init__(self, session: Session):
        self.session = session
        self.deadline_repo = DeadlineRepository(session)

    def evaluate_status(self, deadline: Deadline, current_date: Optional[date] = None) -> str:
        """Determines the current state machine status: upcoming, overdue, or completed."""
        if deadline.status == "completed" or deadline.status == "dismissed":
            return deadline.status
        today = current_date or date.today()
        if deadline.due_date < today:
            return "overdue"
        return "upcoming"

    def sync_all_statuses(self, workspace_id: str) -> None:
        """Updates overdue/upcoming status across all active deadlines in workspace."""
        today = date.today()
        deadlines = self.deadline_repo.list_by_workspace(workspace_id, status=None)
        for dl in deadlines:
            new_status = self.evaluate_status(dl, today)
            if dl.status != new_status and dl.status not in ["completed", "dismissed"]:
                dl.status = new_status
        self.session.commit()

    def create_deadline_for_document(self, doc: Document) -> Optional[Deadline]:
        """Automatically provisions a deadline obligation when a document with an expiry date is saved."""
        if not doc.expiry_date:
            return None

        title = f"{doc.title} Expiry / Renewal"
        deadline = Deadline(
            workspace_id=doc.workspace_id,
            document_id=doc.id,
            title=title,
            due_date=doc.expiry_date,
            priority="high" if doc.category in ["insurance", "identity"] else "medium",
            status="upcoming",
            renewal_cost=doc.renewal_cost or 0.0,
            recurrence_rule="FREQ=YEARLY;INTERVAL=1" if doc.auto_renew else None,
        )
        self.session.add(deadline)
        self.session.flush()

        # Add default multi-interval reminder schedules: 30d, 7d, 1d, 0d
        for days in [30, 7, 1, 0]:
            schedule = ReminderSchedule(
                deadline_id=deadline.id,
                days_before=days,
                channel="in_app",
            )
            self.session.add(schedule)

        self.session.commit()
        return deadline

    def complete_deadline(self, deadline_id: str, workspace_id: str) -> Optional[Deadline]:
        """Marks a deadline as completed and rolls over to the next occurrence if recurring."""
        deadline = self.deadline_repo.get_by_id_scoped(deadline_id, workspace_id)
        if not deadline:
            return None

        deadline.status = "completed"
        deadline.last_evaluated_at = datetime.now(timezone.utc)

        # Handle recurrence rollover
        next_deadline = None
        if deadline.recurrence_rule:
            # Simple RFC 5545 interval parsing
            next_date = deadline.due_date
            if "YEARLY" in deadline.recurrence_rule:
                try:
                    next_date = next_date.replace(year=next_date.year + 1)
                except ValueError:
                    next_date = next_date + timedelta(days=365)
            elif "MONTHLY" in deadline.recurrence_rule:
                # Add 30 days approximation
                next_date = next_date + timedelta(days=30)
            elif "WEEKLY" in deadline.recurrence_rule:
                next_date = next_date + timedelta(days=7)

            next_deadline = Deadline(
                workspace_id=deadline.workspace_id,
                document_id=deadline.document_id,
                title=deadline.title,
                due_date=next_date,
                recurrence_rule=deadline.recurrence_rule,
                priority=deadline.priority,
                status="upcoming",
                renewal_cost=deadline.renewal_cost,
                notes=deadline.notes,
            )
            self.session.add(next_deadline)
            self.session.flush()

            for days in [30, 7, 1, 0]:
                self.session.add(ReminderSchedule(deadline_id=next_deadline.id, days_before=days, channel="in_app"))

        self.session.commit()
        return next_deadline or deadline

    def export_icalendar(self, workspace_id: str) -> str:
        """Generates an RFC 5545 compliant iCalendar feed string."""
        deadlines = self.deadline_repo.list_by_workspace(workspace_id, status=None)
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//LifeLedger//Deadline Intelligence Platform//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "X-WR-CALNAME:LifeLedger Deadlines",
        ]

        now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        for dl in deadlines:
            due_str = dl.due_date.strftime("%Y%m%d")
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:lifeledger-dl-{dl.id}@lifeledger.internal",
                f"DTSTAMP:{now_str}",
                f"DTSTART;VALUE=DATE:{due_str}",
                f"DTEND;VALUE=DATE:{due_str}",
                f"SUMMARY:{dl.title}",
                f"DESCRIPTION:Priority: {dl.priority.upper()}\\nCost: ${dl.renewal_cost:,.2f}",
                f"STATUS:{'CONFIRMED' if dl.status != 'completed' else 'COMPLETED'}",
                "END:VEVENT",
            ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)
