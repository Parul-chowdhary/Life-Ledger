"""
LifeLedger Web Presentation Controller.
Handles HTTP request routing, template rendering, session cookie extraction,
file upload ingestion, and administrative views.
"""
from datetime import date, datetime
import functools
import io
from typing import Optional
from flask import (
    Blueprint, Response, current_app, flash, g, make_response,
    redirect, render_template, request, send_file, url_for
)
from lifeledger_core.exceptions import LifeLedgerException
from lifeledger_models.entities.document import Document, DocumentVersion
from lifeledger_repositories.asset_repository import AssetRepository
from lifeledger_repositories.audit_repository import AuditRepository
from lifeledger_repositories.deadline_repository import DeadlineRepository
from lifeledger_repositories.document_repository import DocumentRepository
from lifeledger_services.admin_service import AdminService
from lifeledger_services.analytics_service import AnalyticsService
from lifeledger_services.asset_service import AssetService
from lifeledger_services.auth_service import AuthService
from lifeledger_services.deadline_service import DeadlineService
from lifeledger_services.ocr_service import OCRService
from lifeledger_services.pdf_report_generator import PDFReportGenerator
from lifeledger_services.storage_service import StorageService

web_bp = Blueprint("web", __name__, template_folder="../templates", static_folder="../static")


def get_db_session():
    """Retrieves the request-scoped SQLAlchemy database session."""
    return current_app.extensions["sqlalchemy_session"]()


def get_current_user():
    """Validates session token from secure cookie."""
    token = request.cookies.get("lifeledger_session")
    if not token:
        return None
    session = get_db_session()
    auth_service = AuthService(session)
    return auth_service.validate_session(token)


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash("Please sign in to access your vault", "warning")
            return redirect(url_for("web.login"))
        g.user = user
        return f(*args, **kwargs)
    return decorated_function


@web_bp.context_processor
def inject_global_template_vars():
    user = get_current_user()
    return {
        "current_user": user,
        "today": date.today(),
        "now": datetime.utcnow(),
    }


# 1. Landing Page
@web_bp.route("/")
def landing():
    user = get_current_user()
    if user:
        return redirect(url_for("web.dashboard"))
    return render_template("landing.html")


# 2. Authentication Views
@web_bp.route("/auth/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        session = get_db_session()
        auth_service = AuthService(session)
        audit_repo = AuditRepository(session)

        try:
            user, session_model = auth_service.authenticate(
                email, password, ip=request.remote_addr, ua=request.headers.get("User-Agent")
            )
            audit_repo.log_event(
                action="auth.login_success",
                resource_type="session",
                resource_id=session_model.id,
                user_id=user.id,
                ip_address=request.remote_addr,
            )
            session.commit()

            resp = make_response(redirect(url_for("web.dashboard")))
            resp.set_cookie(
                "lifeledger_session",
                session_model.token,
                httponly=True,
                samesite="Lax",
                max_age=14 * 86400,
            )
            flash(f"Welcome back, {user.full_name}!", "success")
            return resp
        except LifeLedgerException as e:
            flash(e.message, "danger")

    return render_template("auth/login.html")


@web_bp.route("/auth/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        session = get_db_session()
        auth_service = AuthService(session)

        try:
            user, workspace = auth_service.register_user(email, password, full_name)
            flash("Account and encrypted personal vault created successfully! Please log in.", "success")
            return redirect(url_for("web.login"))
        except LifeLedgerException as e:
            flash(e.message, "danger")

    return render_template("auth/register.html")


@web_bp.route("/auth/logout")
def logout():
    token = request.cookies.get("lifeledger_session")
    if token:
        session = get_db_session()
        auth_service = AuthService(session)
        auth_service.logout(token)

    resp = make_response(redirect(url_for("web.landing")))
    resp.delete_cookie("lifeledger_session")
    flash("You have been signed out safely.", "success")
    return resp


# 3. Main Dashboard Cockpit
@web_bp.route("/dashboard")
@login_required
def dashboard():
    session = get_db_session()
    auth_service = AuthService(session)
    doc_repo = DocumentRepository(session)
    deadline_repo = DeadlineRepository(session)
    analytics_svc = AnalyticsService(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    if not workspace:
        return redirect(url_for("web.logout"))

    metrics = analytics_svc.get_dashboard_metrics(workspace.id)
    recent_docs = doc_repo.list_by_workspace(workspace.id, limit=5)
    upcoming_deadlines = deadline_repo.list_by_workspace(workspace.id, status="upcoming", limit=5)
    urgent_deadlines = [d for d in upcoming_deadlines if (d.due_date - date.today()).days <= 7]

    return render_template(
        "dashboard.html",
        active_page="dashboard",
        metrics=metrics,
        recent_docs=recent_docs,
        upcoming_deadlines=upcoming_deadlines,
        urgent_deadlines=urgent_deadlines,
    )


# 4. Document Vault
@web_bp.route("/vault")
@login_required
def vault():
    session = get_db_session()
    auth_service = AuthService(session)
    doc_repo = DocumentRepository(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    category = request.args.get("category", "all")
    documents = doc_repo.list_by_workspace(workspace.id, category=category)

    return render_template(
        "vault.html",
        active_page="vault",
        documents=documents,
        current_category=category,
    )


# 5. Upload & OCR Review
@web_bp.route("/vault/upload", methods=["GET", "POST"])
@login_required
def upload():
    session = get_db_session()
    auth_service = AuthService(session)
    workspace = auth_service.get_user_default_workspace(g.user.id)

    if request.method == "POST":
        file = request.files.get("file")
        title = request.form.get("title", "")
        category = request.form.get("category", "other")
        issuing_authority = request.form.get("issuing_authority", "")
        expiry_date_str = request.form.get("expiry_date", "")
        renewal_cost_str = request.form.get("renewal_cost", "0")
        auto_renew = request.form.get("auto_renew") == "true"
        is_ice = request.form.get("is_ice_document") == "true"
        notes = request.form.get("notes", "")

        if not file or not title:
            flash("File and document title are required", "danger")
            return redirect(url_for("web.upload"))

        file_bytes = file.read()
        filename = file.filename or "uploaded_document.pdf"
        mime_type = file.mimetype or "application/octet-stream"

        # 1. Encrypt and store file
        storage_svc = StorageService()
        storage_key, sha256_hash, file_size, nonce_hex = storage_svc.store_file(file_bytes, filename)

        # 2. Run OCR Extraction
        ocr_result = OCRService.parse_document(file_bytes, filename, mime_type)

        # Parse expiry date
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        renewal_cost = 0.0
        try:
            renewal_cost = float(renewal_cost_str)
        except ValueError:
            pass

        # 3. Create document record
        doc = Document(
            workspace_id=workspace.id,
            created_by=g.user.id,
            title=title,
            category=category,
            issue_date=date.today(),
            expiry_date=expiry_date,
            issuing_authority=issuing_authority,
            status="active",
            is_ice_document=is_ice,
            renewal_cost=renewal_cost,
            auto_renew=auto_renew,
            notes=notes,
        )
        session.add(doc)
        session.flush()

        # 4. Attach initial version
        version = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            storage_key=storage_key,
            file_name=filename,
            mime_type=mime_type,
            file_size_bytes=file_size,
            sha256_hash=sha256_hash,
            encryption_iv=nonce_hex,
        )
        session.add(version)

        # 5. Automatically create deadline tracker if expiry date exists
        if expiry_date:
            dl_svc = DeadlineService(session)
            dl_svc.create_deadline_for_document(doc)

        session.commit()
        flash(f"Document '{doc.title}' encrypted and safely vaulted!", "success")
        return redirect(url_for("web.vault"))

    return render_template("upload.html", active_page="upload")


# 6. Document Detail & Download
@web_bp.route("/vault/documents/<doc_id>")
@login_required
def view_document(doc_id):
    session = get_db_session()
    auth_service = AuthService(session)
    doc_repo = DocumentRepository(session)
    workspace = auth_service.get_user_default_workspace(g.user.id)

    doc = doc_repo.get_by_id_scoped(doc_id, workspace.id)
    if not doc:
        flash("Document not found", "danger")
        return redirect(url_for("web.vault"))

    return render_template("document_detail.html", active_page="vault", document=doc)


@web_bp.route("/vault/documents/<doc_id>/download")
@login_required
def download_document(doc_id):
    session = get_db_session()
    auth_service = AuthService(session)
    doc_repo = DocumentRepository(session)
    workspace = auth_service.get_user_default_workspace(g.user.id)

    doc = doc_repo.get_by_id_scoped(doc_id, workspace.id)
    if not doc or not doc.versions:
        flash("File unavailable", "danger")
        return redirect(url_for("web.vault"))

    latest = doc.versions[0]
    storage_svc = StorageService()
    file_bytes = storage_svc.retrieve_file(latest.storage_key, latest.encryption_iv)

    return send_file(
        io.BytesIO(file_bytes),
        mimetype=latest.mime_type,
        as_attachment=True,
        download_name=latest.file_name,
    )


# 7. Deadlines View
@web_bp.route("/deadlines")
@login_required
def deadlines():
    session = get_db_session()
    auth_service = AuthService(session)
    dl_repo = DeadlineRepository(session)
    dl_svc = DeadlineService(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    dl_svc.sync_all_statuses(workspace.id)
    all_deadlines = dl_repo.list_by_workspace(workspace.id, status=None)

    return render_template(
        "deadlines.html",
        active_page="deadlines",
        deadlines=all_deadlines,
    )


# 8. Assets & Warranties View
@web_bp.route("/assets")
@login_required
def assets():
    session = get_db_session()
    auth_service = AuthService(session)
    asset_repo = AssetRepository(session)
    asset_svc = AssetService(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    all_assets = asset_repo.list_by_workspace(workspace.id)

    cards = []
    for a in all_assets:
        w_status = asset_svc.calculate_warranty_status(a)
        cards.append({"asset": a, "warranty_status": w_status})

    return render_template("assets.html", active_page="assets", asset_cards=cards)


# 9. Analytics & Cash Flow View
@web_bp.route("/analytics")
@login_required
def analytics():
    session = get_db_session()
    auth_service = AuthService(session)
    analytics_svc = AnalyticsService(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    metrics = analytics_svc.get_dashboard_metrics(workspace.id)
    forecast = analytics_svc.get_12_month_cashflow_forecast(workspace.id)
    category_dist = analytics_svc.get_category_distribution(workspace.id)

    return render_template(
        "analytics.html",
        active_page="analytics",
        metrics=metrics,
        forecast=forecast,
        category_dist=category_dist,
    )


@web_bp.route("/analytics/export-csv")
@login_required
def export_csv():
    session = get_db_session()
    auth_service = AuthService(session)
    analytics_svc = AnalyticsService(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    csv_data = analytics_svc.export_csv(workspace.id)

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=lifeledger-vault-export.csv"},
    )


@web_bp.route("/analytics/export-pdf")
@login_required
def export_pdf():
    session = get_db_session()
    auth_service = AuthService(session)
    analytics_svc = AnalyticsService(session)
    doc_repo = DocumentRepository(session)
    dl_repo = DeadlineRepository(session)

    workspace = auth_service.get_user_default_workspace(g.user.id)
    metrics = analytics_svc.get_dashboard_metrics(workspace.id)
    documents = doc_repo.list_by_workspace(workspace.id)
    deadlines = dl_repo.list_by_workspace(workspace.id)

    doc_dicts = [
        {
            "title": d.title,
            "category": d.category,
            "issuing_authority": d.issuing_authority,
            "expiry_date": d.expiry_date.isoformat() if d.expiry_date else None,
            "is_ice_document": d.is_ice_document,
        }
        for d in documents
    ]
    dl_dicts = [
        {
            "title": dl.title,
            "due_date": dl.due_date.isoformat() if dl.due_date else None,
            "priority": dl.priority,
            "renewal_cost": float(dl.renewal_cost) if dl.renewal_cost else 0.0,
            "status": dl.status,
        }
        for dl in deadlines
    ]

    pdf_bytes = PDFReportGenerator.generate_vault_report(
        workspace_name=workspace.name,
        owner_name=g.user.full_name,
        metrics=metrics,
        documents=doc_dicts,
        deadlines=dl_dicts,
    )

    clean_name = "".join(c if c.isalnum() else "-" for c in workspace.name.lower()).strip("-")
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"lifeledger-audit-{clean_name}.pdf",
    )


# 10. Admin Governance View
@web_bp.route("/admin")
@login_required
def admin():
    if g.user.role != "admin":
        flash("Administrative privileges required", "danger")
        return redirect(url_for("web.dashboard"))

    session = get_db_session()
    admin_svc = AdminService(session)
    health = admin_svc.get_system_health()
    users = admin_svc.list_users()
    audit_logs = admin_svc.list_audit_trail()

    return render_template(
        "admin.html",
        active_page="admin",
        health=health,
        users=users,
        audit_logs=audit_logs,
    )


@web_bp.route("/admin/users/<user_id>/toggle", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    if g.user.role != "admin":
        flash("Unauthorized", "danger")
        return redirect(url_for("web.dashboard"))

    session = get_db_session()
    admin_svc = AdminService(session)
    u = admin_svc.user_repo.get_by_id(user_id)
    if u:
        admin_svc.set_user_status(user_id, not u.is_active, g.user.id)
        flash(f"User {u.full_name} status toggled.", "success")
    return redirect(url_for("web.admin"))
