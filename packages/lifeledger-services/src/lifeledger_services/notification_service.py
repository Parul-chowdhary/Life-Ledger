"""
Multi-Channel Notification Dispatcher.
Evaluates reminder schedules, generates responsive HTML email bodies,
dispatches in-app alerts, and suppresses duplicate notifications within 24h windows.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from lifeledger_models.entities.deadline import Deadline, NotificationAttempt, ReminderSchedule
from lifeledger_repositories.deadline_repository import DeadlineRepository


class NotificationService:
    def __init__(self, session: Session):
        self.session = session
        self.deadline_repo = DeadlineRepository(session)
        # In-memory deduplication set for active session
        self._sent_keys: set[str] = set()

    def evaluate_pending_schedules(self, today: Optional[date] = None) -> List[Dict[str, Any]]:
        """Evaluates active reminder schedules and prepares notifications."""
        current_date = today or date.today()
        schedules = self.deadline_repo.get_active_schedules_for_eval(current_date)
        dispatches = []

        for sched in schedules:
            target_date = sched.deadline.due_date - timedelta(days=sched.days_before)
            if target_date <= current_date and not sched.is_dispatched:
                dedup_key = f"{sched.deadline_id}:{sched.days_before}:{current_date.isoformat()}"
                if dedup_key in self._sent_keys:
                    continue

                # Prepare notification payload
                notification = {
                    "schedule_id": sched.id,
                    "deadline_id": sched.deadline.id,
                    "title": sched.deadline.title,
                    "due_date": sched.deadline.due_date.isoformat(),
                    "days_remaining": (sched.deadline.due_date - current_date).days,
                    "cost": sched.deadline.renewal_cost,
                    "channel": sched.channel,
                }
                dispatches.append(notification)
                self._sent_keys.add(dedup_key)

                # Mark schedule dispatched
                sched.is_dispatched = True
                sched.dispatched_at = datetime.now(timezone.utc)

        self.session.commit()
        return dispatches

    @staticmethod
    def render_email_html(deadline_title: str, due_date_str: str, days_left: int, cost: float) -> str:
        """Compiles clean, responsive HTML email alert."""
        urgency_color = "#dc2626" if days_left <= 7 else "#d97706" if days_left <= 30 else "#2563eb"
        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>LifeLedger Renewal Alert</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px;">
  <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="background-color: {urgency_color}; padding: 20px 24px; color: #ffffff;">
      <h2 style="margin: 0; font-size: 20px;">LifeLedger Deadline Alert</h2>
    </div>
    <div style="padding: 24px;">
      <p style="font-size: 16px; color: #1e293b; margin-top: 0;">
        This is an automated intelligence notification regarding an upcoming obligation:
      </p>
      <div style="background-color: #f1f5f9; border-left: 4px solid {urgency_color}; padding: 16px; margin: 20px 0; border-radius: 4px;">
        <h3 style="margin: 0 0 8px 0; color: #0f172a; font-size: 18px;">{deadline_title}</h3>
        <p style="margin: 4px 0; color: #475569;"><strong>Due Date:</strong> {due_date_str} (in {days_left} days)</p>
        <p style="margin: 4px 0; color: #475569;"><strong>Estimated Cost:</strong> ${cost:,.2f}</p>
      </div>
      <p style="color: #64748b; font-size: 14px;">
        Review this record and mark it completed or renew it from your LifeLedger Dashboard.
      </p>
    </div>
  </div>
</body>
</html>
"""
