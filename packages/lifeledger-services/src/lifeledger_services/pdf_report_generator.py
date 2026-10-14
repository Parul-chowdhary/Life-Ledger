"""
PDF Compliance & Vault Audit Report Generator.
Generates institutional, print-ready PDF vault audit reports using ReportLab.
Includes executive summaries, category inventories, urgent obligations, and ICE emergency rosters.
"""
from datetime import date, datetime
import io
from typing import Any, Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PDFReportGenerator:
    """Generates official vault compliance audit PDF reports."""

    @classmethod
    def generate_vault_report(
        cls,
        workspace_name: str,
        owner_name: str,
        metrics: Dict[str, Any],
        documents: List[Dict[str, Any]],
        deadlines: List[Dict[str, Any]],
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            spaceAfter=16,
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=14,
            spaceAfter=8,
        )

        elements = []

        # Header Title
        elements.append(Paragraph("LifeLedger Vault Compliance Audit", title_style))
        today_str = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
        elements.append(
            Paragraph(f"Workspace: <b>{workspace_name}</b> | Owner: {owner_name} | Generated: {today_str}", subtitle_style)
        )

        # 1. Executive Summary Table
        elements.append(Paragraph("1. Executive Summary & Paperwork Health", section_style))
        summary_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Documents", str(metrics.get("total_documents", 0)), "Health Score", f"{metrics.get('health_score', 100)}%"],
            ["30-Day Liability", f"${metrics.get('due_30d_cost', 0):,.2f}", "Active Warranties", str(metrics.get('active_warranties', 0))],
            ["Urgent Deadlines", str(metrics.get("urgent_count", 0)), "Overdue Obligations", str(metrics.get("overdue_count", 0))],
        ]
        t_summary = Table(summary_data, colWidths=[130, 130, 130, 130])
        t_summary.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 12))

        # 2. Upcoming Obligations Table
        elements.append(Paragraph("2. Upcoming Renewal & Deadline Schedule", section_style))
        dl_data = [["Obligation Title", "Due Date", "Priority", "Projected Cost", "Status"]]
        for dl in deadlines[:10]:
            cost_str = f"${dl.get('renewal_cost', 0):,.2f}" if dl.get('renewal_cost') else "N/A"
            dl_data.append([
                dl.get("title", "")[:35],
                str(dl.get("due_date", "")),
                str(dl.get("priority", "medium")).upper(),
                cost_str,
                str(dl.get("status", "upcoming")).upper(),
            ])
        if len(dl_data) == 1:
            dl_data.append(["No active deadlines recorded.", "—", "—", "—", "—"])

        t_dl = Table(dl_data, colWidths=[200, 90, 75, 80, 75])
        t_dl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        elements.append(t_dl)
        elements.append(Spacer(1, 12))

        # 3. Document Inventory Table
        elements.append(Paragraph("3. Document Vault Inventory (Top Records)", section_style))
        doc_data = [["Document Title", "Category", "Issuer", "Expiry Date", "ICE Emergency"]]
        for d in documents[:15]:
            doc_data.append([
                d.get("title", "")[:35],
                str(d.get("category", "")).capitalize(),
                str(d.get("issuing_authority") or "Personal")[:20],
                str(d.get("expiry_date") or "No Expiry"),
                "YES [ICE]" if d.get("is_ice_document") else "No",
            ])
        if len(doc_data) == 1:
            doc_data.append(["No documents in vault.", "—", "—", "—", "—"])

        t_doc = Table(doc_data, colWidths=[180, 85, 110, 85, 60])
        t_doc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ]))
        elements.append(t_doc)

        # Build Document
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
