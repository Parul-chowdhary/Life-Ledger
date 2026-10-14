"""
Analytics, Cash Flow Forecasting, and Compliance Reporting Service.
Aggregates 12-month renewal liabilities, calculates category distributions,
computes personal paperwork health scores, and generates streaming CSV exports.
"""
from collections import defaultdict
from datetime import date, datetime
import io
from typing import Any, Dict, List
from sqlalchemy.orm import Session
from lifeledger_models.entities.asset import Asset
from lifeledger_models.entities.deadline import Deadline
from lifeledger_models.entities.document import Document
from lifeledger_repositories.asset_repository import AssetRepository
from lifeledger_repositories.deadline_repository import DeadlineRepository
from lifeledger_repositories.document_repository import DocumentRepository


class AnalyticsService:
    def __init__(self, session: Session):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.deadline_repo = DeadlineRepository(session)
        self.asset_repo = AssetRepository(session)

    def get_dashboard_metrics(self, workspace_id: str) -> Dict[str, Any]:
        """Calculates high-level cockpit metrics for dashboard tiles."""
        docs = self.doc_repo.list_by_workspace(workspace_id)
        deadlines = self.deadline_repo.list_by_workspace(workspace_id, status=None)
        assets = self.asset_repo.list_by_workspace(workspace_id)

        today = date.today()
        due_30d_cost = 0.0
        urgent_count = 0
        overdue_count = 0

        for dl in deadlines:
            if dl.status in ["upcoming", "overdue"]:
                days_left = (dl.due_date - today).days
                if days_left < 0:
                    overdue_count += 1
                elif days_left <= 30:
                    due_30d_cost += (dl.renewal_cost or 0.0)
                    if days_left <= 7:
                        urgent_count += 1

        active_warranties = 0
        total_warranty_value = 0.0
        for a in assets:
            if a.warranty_expiry_date and a.warranty_expiry_date >= today:
                active_warranties += 1
                total_warranty_value += (a.purchase_price or 0.0)

        # Health score calculation
        total_docs = len(docs)
        if total_docs == 0:
            health_score = 100
        else:
            missing_dates = sum(1 for d in docs if not d.expiry_date and d.category in ["insurance", "warranty", "bill"])
            penalty = (missing_dates * 8) + (overdue_count * 15)
            health_score = max(35, min(100, 100 - penalty))

        return {
            "total_documents": total_docs,
            "due_30d_cost": round(due_30d_cost, 2),
            "urgent_count": urgent_count,
            "overdue_count": overdue_count,
            "active_warranties": active_warranties,
            "total_warranty_value": round(total_warranty_value, 2),
            "health_score": health_score,
        }

    def get_12_month_cashflow_forecast(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Projects monthly renewal liability for the next 12 months."""
        deadlines = self.deadline_repo.list_by_workspace(workspace_id, status=None)
        today = date.today()

        monthly_buckets: Dict[str, float] = defaultdict(float)
        # Initialize next 12 months
        year = today.year
        month = today.month

        month_labels = []
        for i in range(12):
            cur_m = ((month - 1 + i) % 12) + 1
            cur_y = year + ((month - 1 + i) // 12)
            key = f"{cur_y}-{cur_m:02d}"
            label = datetime(cur_y, cur_m, 1).strftime("%b %Y")
            monthly_buckets[key] = 0.0
            month_labels.append({"key": key, "label": label})

        for dl in deadlines:
            if dl.due_date and dl.renewal_cost:
                key = f"{dl.due_date.year}-{dl.due_date.month:02d}"
                if key in monthly_buckets:
                    monthly_buckets[key] += dl.renewal_cost

        return [
            {"month": m["label"], "key": m["key"], "amount": round(monthly_buckets[m["key"]], 2)}
            for m in month_labels
        ]

    def get_category_distribution(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Returns document counts grouped by category."""
        docs = self.doc_repo.list_by_workspace(workspace_id)
        counts: Dict[str, int] = defaultdict(int)
        for d in docs:
            counts[d.category] += 1

        total = max(1, len(docs))
        return [
            {
                "category": cat.capitalize(),
                "count": count,
                "percentage": round((count / total) * 100, 1)
            }
            for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)
        ]

    def export_csv(self, workspace_id: str) -> str:
        """Generates a comma-separated export of all vault documents and deadlines."""
        docs = self.doc_repo.list_by_workspace(workspace_id)
        output = io.StringIO()
        output.write("ID,Title,Category,IssueDate,ExpiryDate,IssuingAuthority,Status,RenewalCost,AutoRenew\n")

        for d in docs:
            issue_str = d.issue_date.isoformat() if d.issue_date else ""
            expiry_str = d.expiry_date.isoformat() if d.expiry_date else ""
            output.write(
                f'"{d.id}","{d.title}","{d.category}","{issue_str}","{expiry_str}",'
                f'"{d.issuing_authority or ""}","{d.status}",{d.renewal_cost or 0.0},{d.auto_renew}\n'
            )
        return output.getvalue()
