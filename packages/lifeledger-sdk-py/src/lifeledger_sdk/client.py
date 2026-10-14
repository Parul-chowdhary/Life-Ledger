"""
LifeLedger Core Python Client.
Provides unified HTTP connection pooling, token management,
retry strategies, and sub-client namespace routing.
"""
import io
from typing import Any, Dict, List, Optional
import requests
from lifeledger_sdk.models import (
    AssetRecord, CashFlowBucket, DashboardMetrics, DeadlineRecord,
    DocumentRecord, UserProfile, WarrantyClaimLetter, WarrantyStatusDTO
)


class LifeLedgerSDKError(Exception):
    """Base exception for client SDK errors."""
    def __init__(self, message: str, status_code: int = 500, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class LifeLedgerClient:
    """Primary client for interacting with the LifeLedger Platform."""

    def __init__(self, base_url: str = "http://127.0.0.1:5000", session_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session_token = session_token
        if session_token:
            self.session.cookies.set("lifeledger_session", session_token)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                files=files,
                timeout=30,
            )
            if resp.status_code >= 400:
                raise LifeLedgerSDKError(
                    f"HTTP {resp.status_code} Error: {resp.text}",
                    status_code=resp.status_code,
                    response_body=resp.text,
                )
            return resp
        except requests.RequestException as e:
            raise LifeLedgerSDKError(f"Connection failure to {url}: {str(e)}") from e

    # Health & Ping
    def ping(self) -> Dict[str, Any]:
        resp = self._request("GET", "/api/v1/ping")
        return resp.json()

    # Deadlines Operations
    def complete_deadline(self, deadline_id: str) -> Dict[str, Any]:
        resp = self._request("PATCH", f"/api/v1/deadlines/{deadline_id}/complete")
        return resp.json()

    def export_ical(self) -> str:
        resp = self._request("GET", "/api/v1/deadlines/ical")
        return resp.text

    # OpenAPI Docs
    def get_openapi_spec(self) -> Dict[str, Any]:
        resp = self._request("GET", "/api/v1/docs")
        return resp.json()

    # Document Export
    def export_vault_csv(self) -> str:
        resp = self._request("GET", "/analytics/export-csv")
        return resp.text
