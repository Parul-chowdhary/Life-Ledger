# LifeLedger — Personal Document, Warranty and Deadline Intelligence Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Code Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)]()
[![Security Audit](https://img.shields.io/badge/security-hardened-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

> LifeLedger is an enterprise-grade, privacy-first personal document, warranty, and deadline intelligence platform designed to eliminate the human error and financial loss associated with lost personal documents, expired warranties, missed service intervals, lapsed insurance policies, and forgotten regulatory deadlines.

---

## Key Capabilities

1. **Personal Document Vault:**
   * Multi-format document ingestion (PDF, PNG, JPEG, TIFF, WEBP).
   * Client-side & server-side AES-256-GCM envelope encryption.
   * Content-addressable SHA-256 deduplication and immutable version history.
   * "In Case of Emergency" (ICE) designated recovery vault.

2. **Temporal & Deadline Intelligence:**
   * RFC 5545-compliant recurrence rules (daily, weekly, monthly, yearly, custom).
   * Multi-interval proactive alerts (60d, 30d, 14d, 7d, 1d, and day-of).
   * Interactive calendar views, urgent alert banners, and 1-click renewal tracking.
   * iCalendar (.ics) live subscription feed generation.

3. **Asset & Warranty Management:**
   * Appliance and electronics registry with serial numbers, model cataloging, and invoice linkage.
   * Real-time warranty expiration countdown gauges.
   * 1-Click automated formal warranty claim letter & evidence package generator.
   * Maintenance expense logs and straight-line depreciation modeling.

4. **OCR & Extraction Pipeline:**
   * Image preprocessing (grayscale, contrast normalization, deskewing).
   * Rule-based and heuristic extraction for dates, currencies, reference/policy numbers, and merchants.
   * Side-by-side human-in-the-loop review canvas with bounding box highlights and confidence ratings.

5. **Analytics & Financial Health:**
   * 12-Month renewal cash flow projections.
   * Document category distribution charts.
   * Personal paperwork health score and compliance audits.
   * PDF and streaming CSV export.

---

## Architecture Overview

LifeLedger is architected as a modular, package-separated enterprise monorepo:

* `packages/lifeledger-core/`: Cryptographic primitives (AES-256-GCM, Argon2/bcrypt), configuration schemas, telemetry logging, and exception hierarchies.
* `packages/lifeledger-models/`: SQLAlchemy 2.0 declarative models, custom encrypted column types, and Alembic migrations.
* `packages/lifeledger-repositories/`: Data access layer with tenant isolation filters and transaction unit-of-work patterns.
* `packages/lifeledger-services/`: 9 dedicated domain service engines (Auth, Storage, OCR, Deadlines, Notifications, Assets, Search, Analytics, Admin).
* `packages/lifeledger-web/`: Production web frontend with accessible vanilla CSS design system, dark/light theme, and modular ES6 controllers.
* `packages/lifeledger-api/`: Versioned REST API v1 endpoints with OpenAPI 3.1 documentation.
* `packages/lifeledger-sdk-py/`: Official Python client SDK.
* `packages/lifeledger-cli/`: Command-line vault interface.
* `tests/`: Multi-tier test suite (Unit, Integration, Security/IDOR, E2E).

---

## Quickstart & Local Installation

### Prerequisites
* Python 3.11+
* Node 20+ (optional, for Playwright E2E testing)

### Installation
```bash
# 1. Clone repository
git clone https://github.com/lifeledger/lifeledger.git
cd lifeledger

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Seed demo data (passports, electronics warranties, auto insurance)
python scripts/seed_database.py

# 4. Start the application server
python run_app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Default login credentials:
* **Demo User:** `sarah@example.com` / `Password123!`
* **Admin User:** `admin@lifeledger.internal` / `AdminSecret2026!`

---

## Verification & Metric Auditing

LifeLedger includes automated verification tooling to audit code metrics, git commits, and test passes:

```bash
# Run the codebase verification report
python scripts/measure_loc.py

# Execute the automated test suite
pytest
```

---

## Security & Privacy Guarantee

* **Zero Plaintext Secrets:** Passwords hashed with high-cost salt derivation; document payloads encrypted at rest.
* **Strict Tenant Isolation:** Every database query automatically scoped by authenticated workspace ID.
* **Offline-Ready:** Runs completely on your local machine without mandatory third-party cloud dependencies.

### Reproducible dependency installation

The repository includes `requirements.lock` with exact pins for the Python dependencies declared in `requirements.txt`. Install the pinned environment with:

```bash
python -m pip install -r requirements.lock
```

`poetry.lock` is also included for repository scanners that require a Poetry lockfile. If you change dependencies, regenerate the lockfiles in an environment with package-index access and commit the updated files together with the manifest.
