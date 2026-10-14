"""
Tests for RRULE Engine, Appliance Catalog, Search Index, and PDF Report Generator.
Validates RFC 5545 recurrence expansions, consumer appliance lifecycle estimates,
Soundex phonetic inverted indexing, and PDF compliance export.
"""
from datetime import date, datetime, timedelta
import pytest
from lifeledger_services.appliance_catalog import APPLIANCE_CATEGORIES, ApplianceCatalog, MANUFACTURER_DIRECTORY
from lifeledger_services.pdf_report_generator import PDFReportGenerator
from lifeledger_services.rrule_engine import RecurrenceRule
from lifeledger_services.search_engine import InvertedIndex, soundex


# =====================================================================
# 1. RRULE Engine Tests
# =====================================================================

def test_rrule_parsing_and_serialization():
    rule_str = "FREQ=MONTHLY;INTERVAL=2;COUNT=5"
    rule = RecurrenceRule.from_string(rule_str)
    assert rule.freq == "MONTHLY"
    assert rule.interval == 2
    assert rule.count == 5

    serialized = rule.to_string()
    assert "FREQ=MONTHLY" in serialized
    assert "INTERVAL=2" in serialized
    assert "COUNT=5" in serialized


def test_rrule_occurrences_generation():
    start = date(2026, 1, 1)
    rule = RecurrenceRule(freq="MONTHLY", interval=1, count=4)
    occurrences = list(rule.generate_occurrences(start))
    assert len(occurrences) == 4
    assert occurrences[0] == date(2026, 1, 1)
    assert occurrences[1] == date(2026, 2, 1)
    assert occurrences[2] == date(2026, 3, 1)
    assert occurrences[3] == date(2026, 4, 1)


def test_rrule_next_occurrence():
    start = date(2026, 1, 15)
    rule = RecurrenceRule(freq="YEARLY", interval=1)
    next_date = rule.get_next_occurrence(start, after_date=date(2026, 6, 1))
    assert next_date == date(2027, 1, 15)


def test_rrule_invalid_frequency():
    with pytest.raises(ValueError):
        RecurrenceRule(freq="MINUTELY")


# =====================================================================
# 2. Appliance Catalog Intelligence Tests
# =====================================================================

def test_appliance_catalog_lookup():
    fridge_info = ApplianceCatalog.get_category_info("refrigerator")
    assert fridge_info is not None
    assert fridge_info["expected_lifespan_years"] == 12
    assert fridge_info["default_warranty_months"] == 12

    unknown = ApplianceCatalog.get_category_info("hovercraft")
    assert unknown is None


def test_appliance_manufacturer_directory():
    apple_support = ApplianceCatalog.get_manufacturer_support("Apple")
    assert apple_support is not None
    assert "1-800" in apple_support["support_phone"]
    assert "AppleCare+" in apple_support["extended_warranty_name"]


def test_appliance_replacement_estimate():
    install_date = date(2020, 5, 1)
    est_date, is_end_of_life = ApplianceCatalog.estimate_replacement_date("dishwasher", install_date)
    assert est_date.year == 2029
    assert est_date.month == 5
    assert not is_end_of_life

    # Older install date -> past expected lifespan
    old_install = date(2005, 1, 1)
    old_est, old_eol = ApplianceCatalog.estimate_replacement_date("dishwasher", old_install)
    assert old_eol is True


# =====================================================================
# 3. Soundex & Search Engine Inverted Index Tests
# =====================================================================

def test_soundex_phonetic_hashing():
    # Robert and Rupert should yield identical Soundex codes
    assert soundex("Robert") == soundex("Rupert")
    # Smith and Smyth / Smythe
    assert soundex("Smith") == soundex("Smythe")
    assert soundex("") == "0000"


def test_inverted_index_indexing_and_search():
    index = InvertedIndex()
    index.add_document("doc-1", {
        "title": "Geico Auto Comprehensive Policy",
        "category": "insurance",
        "notes": "Vehicle identification number check and renewal notice",
    })
    index.add_document("doc-2", {
        "title": "AppleCare Protection Plan MacBook Pro",
        "category": "warranty",
        "notes": "Hardware repairs and battery replacement plan",
    })

    # Exact token search
    results_geico = index.search("Geico")
    assert len(results_geico) >= 1
    assert results_geico[0]["doc_id"] == "doc-1"

    # Multi-term query
    results_apple = index.search("MacBook battery")
    assert len(results_apple) >= 1
    assert results_apple[0]["doc_id"] == "doc-2"

    # Phonetic Soundex match: "Geyko" -> matches "Geico"
    results_phonetic = index.search("Geyko")
    assert any(r["doc_id"] == "doc-1" for r in results_phonetic)


# =====================================================================
# 4. PDF Compliance Report Generator Tests
# =====================================================================

def test_pdf_report_generator_bytes():
    pdf_bytes = PDFReportGenerator.generate_vault_report(
        workspace_name="Household Main",
        owner_name="Sarah Jenkins",
        metrics={"total_documents": 5, "health_score": 95, "due_30d_cost": 210.0, "active_warranties": 3, "urgent_count": 1, "overdue_count": 0},
        documents=[
            {"title": "Tesla Model Y Title", "category": "vehicle", "issuing_authority": "DMV", "expiry_date": "2030-01-01", "is_ice_document": True}
        ],
        deadlines=[
            {"title": "Auto Insurance Renewal", "due_date": "2026-10-18", "priority": "urgent", "renewal_cost": 180.0, "status": "upcoming"}
        ],
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF-")


# =====================================================================
# 5. Web Route PDF Export Integration Test
# =====================================================================

def test_web_analytics_export_pdf(client):
    # Authenticate as seeded demo user
    client.post("/auth/login", data={"email": "sarah@example.com", "password": "Password123!"})

    resp = client.get("/analytics/export-pdf")
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    assert resp.data.startswith(b"%PDF-")
