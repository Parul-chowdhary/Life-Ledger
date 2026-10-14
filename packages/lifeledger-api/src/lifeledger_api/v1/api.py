"""
LifeLedger REST API v1 Blueprint.
Exposes JSON endpoints for authentication, vault documents, deadlines,
assets, iCalendar feed export, and OpenAPI 3.1 documentation.
"""
from datetime import date
from flask import Blueprint, Response, current_app, jsonify, request
from lifeledger_services.analytics_service import AnalyticsService
from lifeledger_services.asset_service import AssetService
from lifeledger_services.auth_service import AuthService
from lifeledger_services.deadline_service import DeadlineService
from lifeledger_services.storage_service import StorageService

api_v1_bp = Blueprint("api_v1", __name__)


def get_db():
    return current_app.extensions["sqlalchemy_session"]()


@api_v1_bp.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "healthy", "service": "LifeLedger REST API v1"})


@api_v1_bp.route("/deadlines/<deadline_id>/complete", methods=["PATCH"])
def complete_deadline(deadline_id):
    session = get_db()
    dl_svc = DeadlineService(session)

    # Find deadline
    from lifeledger_models.entities.deadline import Deadline
    dl = session.get(Deadline, deadline_id)
    if not dl:
        return jsonify({"error": "Deadline not found"}), 404

    updated = dl_svc.complete_deadline(deadline_id, dl.workspace_id)
    return jsonify({
        "success": True,
        "deadline_id": deadline_id,
        "status": "completed",
        "next_occurrence": updated.due_date.isoformat() if updated != dl else None,
    })


@api_v1_bp.route("/deadlines/ical", methods=["GET"])
def export_ical():
    session = get_db()
    auth_service = AuthService(session)
    dl_svc = DeadlineService(session)

    token = request.cookies.get("lifeledger_session")
    user = auth_service.validate_session(token) if token else None

    # Get workspace id
    from lifeledger_models.entities.workspace import Workspace
    ws = session.query(Workspace).first()
    ws_id = ws.id if ws else "default"

    ical_content = dl_svc.export_icalendar(ws_id)
    return Response(
        ical_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=lifeledger-feed.ics"},
    )


@api_v1_bp.route("/docs", methods=["GET"])
def openapi_spec():
    """Returns OpenAPI 3.1 JSON specification."""
    spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "LifeLedger Intelligence Platform API",
            "version": "1.0.0",
            "description": "Secure, zero-knowledge personal document, warranty, and deadline API.",
        },
        "paths": {
            "/api/v1/ping": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "Service is healthy"}}
                }
            },
            "/api/v1/deadlines/{id}/complete": {
                "patch": {
                    "summary": "Mark deadline completed and trigger recurrence rollover",
                    "parameters": [{"name": "id", "in": "path", "required": True}],
                    "responses": {"200": {"description": "Deadline updated"}}
                }
            },
            "/api/v1/deadlines/ical": {
                "get": {
                    "summary": "Export iCalendar .ics stream",
                    "responses": {"200": {"description": "RFC 5545 calendar stream"}}
                }
            }
        }
    }
    return jsonify(spec)
