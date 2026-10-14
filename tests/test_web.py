"""
Web and REST API Endpoint Tests.
Verifies HTTP endpoints, session auth cookies, dashboard view rendering,
vault filtering, and iCalendar feed export.
"""
import pytest


def test_landing_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Never Lose a Document" in response.data


def test_auth_login_workflow(client):
    # Log in as demo user seeded previously
    resp = client.post(
        "/auth/login",
        data={"email": "sarah@example.com", "password": "Password123!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Lifecycle Intelligence Cockpit" in resp.data


def test_dashboard_authenticated(client):
    # Login first
    client.post("/auth/login", data={"email": "sarah@example.com", "password": "Password123!"})
    
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"ACTIVE RECORDS" in resp.data
    assert b"VAULT HEALTH SCORE" in resp.data


def test_vault_view(client):
    client.post("/auth/login", data={"email": "sarah@example.com", "password": "Password123!"})
    
    resp = client.get("/vault")
    assert resp.status_code == 200
    assert b"Encrypted Document Vault" in resp.data
    assert b"Geico Automobile Comprehensive Insurance" in resp.data


def test_deadlines_and_ical_export(client):
    client.post("/auth/login", data={"email": "sarah@example.com", "password": "Password123!"})

    resp = client.get("/deadlines")
    assert resp.status_code == 200
    assert b"Deadline" in resp.data and b"Renewal Intelligence" in resp.data

    # Test iCal export
    resp_ical = client.get("/api/v1/deadlines/ical")
    assert resp_ical.status_code == 200
    assert b"BEGIN:VCALENDAR" in resp_ical.data


def test_api_ping_and_docs(client):
    ping_resp = client.get("/api/v1/ping")
    assert ping_resp.status_code == 200
    assert ping_resp.json["status"] == "healthy"

    docs_resp = client.get("/api/v1/docs")
    assert docs_resp.status_code == 200
    assert "openapi" in docs_resp.json
