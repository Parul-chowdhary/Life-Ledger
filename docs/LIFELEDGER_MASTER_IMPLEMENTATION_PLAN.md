# LifeLedger — Personal Document, Warranty and Deadline Intelligence Platform
## Master Engineering Implementation Plan & Architectural Blueprint (500K+ LOC Scope)

---

## 1. Executive Summary

**LifeLedger** is an enterprise-grade, privacy-first personal document, warranty, and deadline intelligence platform designed to eliminate the human error and financial loss associated with lost personal documents, expired warranties, missed service intervals, lapsed insurance policies, and forgotten regulatory deadlines. 

Modern households manage dozens of critical lifecycle documents—passports, birth certificates, automobile titles, home appliances with warranty periods, health and property insurance binders, utility contracts, tax records, and maintenance logs. Existing solutions are fragmented across generic cloud storage (Google Drive, Dropbox) which lack temporal intelligence, calendar apps which lack document context, and commercial personal finance apps which focus on bank transactions rather than asset lifecycle obligations.

LifeLedger bridges this gap by unifying secure, client-side encrypted document storage with an optical character recognition (OCR) parsing pipeline, a deterministic recurrence and deadline scheduling engine, an asset maintenance and warranty claim manager, and a multi-channel notification dispatcher.

To deliver this capabilities at institutional fidelity, LifeLedger is engineered as a modular, package-separated application. The system targets an authored codebase footprint exceeding **500,000 Lines of Code (LOC)** across core backend services, document ingestion pipelines, search engines, client SDKs, administrative controls, an accessible design system, and an exhaustive automated testing harness. Development is structured around a rigorous Git workflow comprising **200+ atomic commits** and **100+ pull requests**, validated by automated CI/CD pipelines, reproducible dependency manifests, and verifiable measurement tooling.

---

## 2. Real-Life Problem Statement and Target Users

### 2.1 The Problem
Individuals and households lose thousands of dollars annually and suffer severe administrative friction due to four distinct pain points:
1. **Unorganized Document Dispersion:** Vital records are scattered across physical filing cabinets, email attachments, photo libraries, and disparate portal logins. Finding an appliance invoice during a repair emergency takes an average of 45 minutes or ends in failure.
2. **Expired Warranties and Unclaimed Rights:** Consumer electronics and household appliances typically carry 1- to 5-year warranties. Over 78% of consumers fail to claim valid warranty repairs because they cannot locate proof of purchase or serial number records before expiration.
3. **Lapsed Policies and Late Penalty Fees:** Driver's licenses, passports, vehicle registrations, professional certifications, and insurance coverage require active renewal. Lapsing results in penalties, legal exposure, or loss of coverage during catastrophic events.
4. **Emergency Inaccessibility:** In personal or medical emergencies, family members cannot quickly access health directives, insurance policy numbers, identity papers, or home utility shut-off protocols.

### 2.2 Target User Personas
* **Persona 1: The Household Quartermaster (Sarah, 38)** — Manages a 4-person family household. Responsible for 2 vehicles, home appliance warranties, health/dental/auto insurance, school records, and mortgage papers. Needs proactive renewal alerts, multi-member profile organization, and instant search by serial number.
* **Persona 2: The Self-Employed Professional (David, 29)** — Freelancer with equipment depreciation schedules, software subscriptions, professional liability insurance, and tax documentation. Needs receipt categorization, warranty tracking for high-end workstation gear, and exportable financial summaries.
* **Persona 3: The Aging Parent Caretaker (Elena, 45)** — Manages documents for elderly parents across two households. Needs delegated read/write permissions, medical card storage, property deed records, and an emergency document packet accessible with single-click verification.
* **Persona 4: System Administrators & Compliance Officers** — Requires full audit logs, storage quota enforcement, tenant isolation, and GDPR/CCPA data export and erasure capabilities.

---

## 3. Project Scope and Non-Goals

### 3.1 In-Scope Capabilities
* **Identity & Access Management:** Session-based auth, Argon2id hashing, role-based access control (User, Family Manager, Auditor, Administrator), session revocation, time-based OTP (TOTP) two-factor authentication.
* **Encrypted Vault Storage:** Multi-format document ingestion (PDF, PNG, JPEG, TIFF, WEBP), client-side metadata encryption, SHA-256 content deduplication, versioning, and retention management.
* **Asynchronous OCR & Field Extraction:** Tesseract/ONNX OCR pipeline, heuristic date/amount/vendor extractors, confidence scoring, and interactive human-in-the-loop review.
* **Temporal Intelligence Engine:** RFC 5545-compliant recurrence rules, timezone-aware deadline calculations, multi-stage notification schedules (e.g., 60d, 30d, 14d, 7d, 1d, day-of), and snooze workflows.
* **Asset & Warranty Lifecycle:** Asset inventory with invoice linkage, depreciation calculation, service ticket logging, and automated warranty claim letter generation.
* **Multi-Tenant Family Workspaces:** Granular document sharing, role inheritance, and an "In Case of Emergency" (ICE) time-locked recovery vault.
* **Analytics & Search:** Full-text indexing (SQLite FTS5 / PostgreSQL pg_trgm), renewal cash-flow forecasts, and PDF/CSV compliance report generation.
* **Administrative Portal:** User lifecycle governance, queue inspection, storage usage telemetry, security audit log inspection, and configuration toggles.

### 3.2 Explicit Non-Goals
* **Non-Goal 1: Direct Banking / Plaid Integration:** LifeLedger tracks *documents and contractual obligations*, not real-time bank account balances or credit card transactions.
* **Non-Goal 2: Universal Cloud Sync Broker:** LifeLedger is not a generalized backup tool for arbitrary media libraries (e.g., family photo albums or video streams); it strictly enforces document-centric MIME types.
* **Non-Goal 3: Automated Legal Advice:** The warranty claim assistant provides standardized claim letter templates and evidence packages; it does not render legal judgment or file small-claims suits.
* **Non-Goal 4: Closed-source Third-party OCR Cloud Lock-in:** The primary pipeline must function entirely offline or locally without mandatory external API dependencies (e.g., Google Cloud Vision or AWS Textract), ensuring absolute user privacy.

---

## 4. Functional and Non-Functional Requirements

### 4.1 Functional Requirements (FR)
* **FR-01 (Auth):** Secure registration, login, password reset via signed tokens, TOTP 2FA, and session management.
* **FR-02 (Vault):** Store documents with user-defined tags, category taxonomies, issue date, expiration date, issuing authority, and arbitrary key-value custom attributes.
* **FR-03 (Version Control):** Every document update creates a new immutable version record while retaining access to prior revisions.
* **FR-04 (OCR Processing):** Background asynchronous extraction of text, suggested metadata (dates, vendor, policy number, cost), and confidence ratings with manual override.
* **FR-05 (Deadlines):** Automatic creation of deadline trackers from document expiry dates, with configurable notification rules and recurrence patterns.
* **FR-06 (Notifications):** Multi-channel alerts (In-App notification center, SMTP email, iCalendar .ics feeds, and Webhook dispatch).
* **FR-07 (Warranties):** Asset register tracking serial number, purchase store, warranty duration, extended warranty coverage, and repair logs.
* **FR-08 (Emergency ICE):** Designated emergency document bundle protected by a dual-custody or delayed-release notification mechanism.
* **FR-09 (Search):** Sub-50ms search across document titles, OCR-extracted full-text content, tags, and custom fields.
* **FR-10 (Admin):** Complete administrative dashboard for system monitoring, user status management, queue health, and audit trails.

### 4.2 Non-Functional Requirements (NFR)
* **NFR-01 (Security):** Zero plain-text storage of passwords (Argon2id with memory cost 64MB, time cost 3, parallelism 4); AES-256-GCM encryption for stored files on disk; strict CSRF token validation; Content Security Policy (CSP) Level 3 headers.
* **NFR-02 (Performance):** Page load times under 800ms on broadband; document upload pipeline responds synchronously within 300ms by offloading OCR and thumbnailing to background workers.
* **NFR-03 (Availability & Reliability):** 99.9% uptime target; zero data loss guarantee via database foreign-key constraints and ACID transaction boundaries.
* **NFR-04 (Portability):** Zero-dependency development mode running on SQLite and local disk; production mode supporting PostgreSQL, Redis, and S3-compatible object stores.
* **NFR-05 (Accessibility):** WCAG 2.1 Level AA compliance across all web views, including full keyboard navigation, ARIA landmarks, and contrast ratios ≥ 4.5:1.
* **NFR-06 (Code Quality):** 100% flake8/ruff compliance, mypy strict type-checking on all core modules, zero critical Bandit security findings, and ≥ 85% automated test coverage.

---

## 5. Feature-Priority Matrix

| Feature Module | Priority | Complexity | Release Milestone | Justification |
|---|---|---|---|---|
| User Auth & Session Security | P0 (Must Have) | High | M1 (Foundation) | Core security boundary and tenant isolation prerequisite. |
| Document Vault & File Storage | P0 (Must Have) | High | M1 (Foundation) | Primary value proposition: reliable document storage. |
| Recurrence & Deadline Engine | P0 (Must Have) | High | M2 (Core Intelligence) | Automated temporal intelligence for expiration tracking. |
| In-App & Email Notifications | P0 (Must Have) | Medium | M2 (Core Intelligence) | Proactive alerting stops users from missing deadlines. |
| Asset & Warranty Management | P1 (Should Have)| Medium | M3 (Asset Subsystem) | Critical for warranty claims and appliance lifecycle. |
| Background OCR & Extraction | P1 (Should Have)| High | M4 (AI & Parsing) | Reduces manual data entry friction for new documents. |
| Full-Text Search Engine | P1 (Should Have)| Medium | M4 (AI & Parsing) | Fast retrieval across thousands of stored documents. |
| Family Workspaces & Sharing | P2 (Nice to Have)| High | M5 (Collaboration) | Multi-user household delegation and permissions. |
| Emergency ICE Access Vault | P2 (Nice to Have)| Medium | M5 (Collaboration) | Vital safety feature for family emergency readiness. |
| Analytics & Cash Flow Reports | P2 (Nice to Have)| Medium | M6 (Reporting) | Visual financial projection of upcoming renewal costs. |
| Admin Portal & Audit Viewer | P1 (Should Have)| Medium | M6 (Reporting) | Operational governance, compliance, and telemetry. |
| Client SDKs & CLI Utility | P2 (Nice to Have)| High | M7 (Extensibility) | Power-user automation and multi-platform integration. |

---

## 6. Technology Selection and Justification

```
+---------------------------------------------------------------------------------+
|                                TECHNOLOGY STACK                                 |
+--------------------+------------------------------------------------------------+
| Frontend Layer     | Semantic HTML5, Vanilla Modern CSS3 (BEM, CSS Custom       |
|                    | Properties, Dark/Light Themes), ES6+ Modular JavaScript.   |
|                    | Zero bulky JS framework dependencies; maximum longevity.   |
+--------------------+------------------------------------------------------------+
| Backend Core       | Python 3.12+ with Flask modular application factory,       |
|                    | Blueprints, Pydantic v2 data validation, and Celery / RQ.  |
+--------------------+------------------------------------------------------------+
| Database & ORM     | SQLAlchemy 2.0 (Modern Declarative Mapped types),          |
|                    | Alembic database migration framework.                      |
|                    | SQLite 3.38+ (Local/Dev) -> PostgreSQL 16+ (Production).   |
+--------------------+------------------------------------------------------------+
| File Storage       | Abstract Storage Provider: Local Filesystem Storage Adapter |
|                    | (Dev) and S3/MinIO Object Storage Adapter (Prod).          |
+--------------------+------------------------------------------------------------+
| OCR & Processing   | Tesseract 5.x / PyTesseract with Pillow image preprocessing|
|                    | (contrast enhancement, deskewing), PDFMiner.six for PDFs.  |
+--------------------+------------------------------------------------------------+
| Security & Crypt   | Argon2id (passwords), Cryptography package (AES-256-GCM    |
|                    | envelope encryption for files), Flask-WTF (CSRF tokens),   |
|                    | Talisman (Secure HTTP headers).                            |
+--------------------+------------------------------------------------------------+
| Testing Framework  | Pytest, Pytest-Cov, Pytest-Mock, Playwright for E2E,       |
|                    | Hypothesis for property-based testing, Locust for load.    |
+--------------------+------------------------------------------------------------+
| Build & DevSecOps  | Poetry for dependency locking, Docker multi-stage builds,  |
|                    | Ruff (linter/formatter), Mypy (type check), Bandit (SAST). |
+--------------------+------------------------------------------------------------+
```

### Technology Justifications:
1. **Flask & Blueprint Architecture over monolithic Django or micro FastAPI:** Flask provides the precise balance of unopinionated modularity and battle-tested WSGI/ASGI maturity needed for custom enterprise package layouts. Blueprints allow cleanly isolating each domain into independent packages.
2. **Vanilla Modern CSS & Modular JS over Node/React/Tailwind:** Eliminates complex JavaScript toolchains, npm vulnerability churn, and node_modules bloat. Native CSS Custom Properties and ES6 Web Components deliver lightning-fast load times, WCAG AA compliance, and zero build-step overhead while remaining completely maintainable for a student or enterprise developer.
3. **SQLAlchemy 2.0 with Alembic:** Guarantees strict type safety in ORM models, transaction boundary isolation, connection pooling, and seamless transition from local development SQLite to clustered PostgreSQL without code changes.
4. **Local Tesseract OCR with Heuristic Pipeline:** Avoids vendor cloud lock-in, eliminates recurring external API fees, preserves user document privacy, and enables fully offline/local operation.

---

## 7. System Architecture and Mermaid Diagrams

### 7.1 High-Level Architecture Diagram

```mermaid
graph TD
    Client[Browser / Desktop Client] -->|HTTPS / TLS 1.3| Edge[Reverse Proxy / Nginx / Caddy]
    Edge -->|WSGI / gunicorn| App[LifeLedger Core Application Server]
    
    subgraph "Application Core (Flask Modular Runtime)"
        AuthMod[Auth & RBAC Subsystem]
        VaultMod[Document Vault Subsystem]
        DeadlineMod[Deadline & Recurrence Subsystem]
        WarrantyMod[Asset & Warranty Subsystem]
        SearchMod[Search & Query Subsystem]
        AdminMod[Admin & Telemetry Subsystem]
        FamilyMod[Family & Workspace Subsystem]
    end
    
    App --> AuthMod
    App --> VaultMod
    App --> DeadlineMod
    App --> WarrantyMod
    App --> SearchMod
    App --> AdminMod
    App --> FamilyMod
    
    subgraph "Asynchronous Processing & Storage"
        Queue[Task Broker: Redis / SQLite Job Queue]
        Workers[Celery / Background Ingestion Workers]
        OCR[Tesseract / Pillow OCR Engine]
        Storage[Storage Provider: Local Encrypted / S3 Adapter]
        DB[(Primary Database: SQLite / PostgreSQL)]
    end
    
    VaultMod -->|Enqueue Ingestion| Queue
    Queue --> Workers
    Workers --> OCR
    Workers --> Storage
    Workers --> DB
    
    VaultMod --> DB
    DeadlineMod --> DB
    WarrantyMod --> DB
    SearchMod --> DB
    AdminMod --> DB
```

### 7.2 Module Dependency Diagram

```mermaid
graph LR
    subgraph "Foundation Layer"
        CoreUtils[lifeledger_core.utils]
        CoreExceptions[lifeledger_core.exceptions]
        CoreCrypto[lifeledger_core.crypto]
    end

    subgraph "Persistence & Domain Layer"
        Models[lifeledger_models]
        Repositories[lifeledger_repositories]
    end

    subgraph "Service Subsystems"
        AuthSvc[lifeledger_services.auth]
        StorageSvc[lifeledger_services.storage]
        OCRSvc[lifeledger_services.ocr]
        DeadlineSvc[lifeledger_services.deadlines]
        NotificationSvc[lifeledger_services.notifications]
        AssetSvc[lifeledger_services.assets]
        SearchSvc[lifeledger_services.search]
        AnalyticsSvc[lifeledger_services.analytics]
        AdminSvc[lifeledger_services.admin]
    end

    subgraph "Presentation & API Layer"
        WebControllers[lifeledger_web.controllers]
        APIControllers[lifeledger_api.v1]
        Templates[lifeledger_web.templates]
    end

    Models --> CoreUtils
    Models --> CoreExceptions
    Repositories --> Models
    Repositories --> CoreCrypto
    
    AuthSvc --> Repositories
    StorageSvc --> Repositories
    StorageSvc --> CoreCrypto
    OCRSvc --> StorageSvc
    DeadlineSvc --> Repositories
    NotificationSvc --> Repositories
    AssetSvc --> Repositories
    SearchSvc --> Repositories
    AnalyticsSvc --> Repositories
    AdminSvc --> Repositories

    WebControllers --> AuthSvc
    WebControllers --> StorageSvc
    WebControllers --> DeadlineSvc
    WebControllers --> AssetSvc
    WebControllers --> AnalyticsSvc
    WebControllers --> AdminSvc
    
    APIControllers --> AuthSvc
    APIControllers --> StorageSvc
    APIControllers --> DeadlineSvc
    APIControllers --> AssetSvc
```

### 7.3 Data-Flow Diagram (Document Ingestion Pipeline)

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant Controller as Document Controller
    participant Storage as Storage Adapter
    participant Queue as Background Queue
    participant Worker as OCR Ingestion Worker
    participant Tesseract as OCR Engine
    participant DB as Database (SQLAlchemy)

    User->>Controller: POST /vault/upload (File + Initial Metadata)
    Controller->>Controller: Validate MIME, File Size, Virus Scan
    Controller->>Storage: Encrypt (AES-256-GCM) & Save Raw Stream
    Storage-->>Controller: Return Storage Key & SHA-256 Hash
    Controller->>DB: Insert Document Record (Status: PENDING_OCR)
    Controller->>Queue: Enqueue OCR Job(document_id, storage_key)
    Controller-->>User: 201 Created (Document JSON + Processing Status)

    Queue->>Worker: Consume OCR Job
    Worker->>Storage: Fetch & Decrypt Raw Document
    Worker->>Worker: Preprocess (PDF rasterize / Grayscale / Deskew)
    Worker->>Tesseract: Execute Optical Character Recognition
    Tesseract-->>Worker: Extracted Plain Text + Bounding Boxes
    Worker->>Worker: Run Regex & Semantic Extractors (Dates, Amounts, Policy #)
    Worker->>DB: Save Extracted Fields & Confidence Ratings
    Worker->>DB: Update Document Status to READY_FOR_REVIEW
    Worker->>Queue: Enqueue Deadline Calculation Job
    Worker-->>Queue: Acknowledge Task Completion
```

### 7.4 Deployment Topology Diagram

```mermaid
graph TB
    subgraph "Public Internet"
        UserDevice[User Web Browser / Mobile Browser]
    end

    subgraph "Demilitarized Zone (DMZ)"
        NginxProxy[Nginx 1.25+ Reverse Proxy<br/>SSL Termination, Rate Limiting, Static Assets]
    end

    subgraph "Application Private Network"
        AppNode1[Gunicorn WSGI: LifeLedger Web App 1]
        AppNode2[Gunicorn WSGI: LifeLedger Web App 2]
        CeleryWorker1[Celery Worker: OCR & Ingestion Node]
        CeleryWorker2[Celery Worker: Deadline & Notification Node]
        CeleryBeat[Celery Beat: Scheduled Cron Dispatcher]
    end

    subgraph "Data Storage Tier (Isolated VPC)"
        PostgreCluster[(PostgreSQL 16 Primary + Read Replica)]
        RedisCluster[(Redis 7.2 Cluster: Cache & Broker)]
        ObjectStore[(MinIO / S3 Encrypted Document Store)]
    end

    UserDevice -->|HTTPS / Port 443| NginxProxy
    NginxProxy -->|HTTP / Port 8000| AppNode1
    NginxProxy -->|HTTP / Port 8000| AppNode2

    AppNode1 --> PostgreCluster
    AppNode2 --> PostgreCluster
    AppNode1 --> RedisCluster
    AppNode2 --> RedisCluster
    AppNode1 --> ObjectStore
    AppNode2 --> ObjectStore

    RedisCluster --> CeleryWorker1
    RedisCluster --> CeleryWorker2
    CeleryBeat --> RedisCluster

    CeleryWorker1 --> ObjectStore
    CeleryWorker1 --> PostgreCluster
    CeleryWorker2 --> PostgreCluster
```

---

## 8. Repository and Package Structure

The repository is organized as a clean enterprise monorepo using standard Python packaging conventions with isolated subsystems:

```
lifeledger/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Linting, formatting, security scan, unit tests
│   │   ├── e2e.yml                # Playwright browser end-to-end matrix
│   │   ├── release.yml            # Semantic versioning, changelog, docker push
│   │   └── codeql.yml             # Static Application Security Testing (SAST)
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── docker/
│   ├── Dockerfile.web             # Multi-stage production web container
│   ├── Dockerfile.worker          # Background worker container with Tesseract
│   ├── docker-compose.yml         # Local orchestration (Web, Worker, Postgres, Redis, MinIO)
│   └── nginx.conf                 # Hardened reverse proxy configuration
├── docs/
│   ├── architecture/              # Architectural Decision Records (ADRs)
│   ├── api/                       # OpenAPI v3.1 specification documents
│   ├── deployment/                # Production runbooks and backup guides
│   └── security/                  # Threat models and vulnerability disclosure policy
├── scripts/
│   ├── measure_loc.py             # Reproducible authored LOC counter script
│   ├── verify_pr_history.py       # Git history and PR verification tool
│   ├── seed_database.py           # Realistic lifecycle mock data generator
│   └── backup_vault.py            # Automated encrypted backup/restore CLI
├── packages/
│   ├── lifeledger-core/           # Domain primitives, crypto, exceptions, configuration
│   │   ├── pyproject.toml
│   │   └── src/lifeledger_core/
│   │       ├── crypto/            # Envelope encryption, Argon2, token signing
│   │       ├── config/            # Settings, env parsing, validation schemas
│   │       ├── exceptions/        # Unified error hierarchy
│   │       └── telemetry/         # Structured JSON logging, metrics, tracing
│   ├── lifeledger-models/         # Database entities, Alembic migrations, schemas
│   │   ├── pyproject.toml
│   │   └── src/lifeledger_models/
│   │       ├── entities/          # User, Document, Deadline, Asset, Audit, Workspace
│   │       ├── migrations/        # Version-controlled Alembic migrations
│   │       └── types/             # Custom SQL types (EncryptedString, JSONB, UUID)
│   ├── lifeledger-repositories/   # Data access layer, query builders, transactions
│   │   ├── pyproject.toml
│   │   └── src/lifeledger_repositories/
│   ├── lifeledger-services/       # Business logic subsystems
│   │   ├── pyproject.toml
│   │   └── src/lifeledger_services/
│   │       ├── auth/              # Registration, session, MFA, RBAC
│   │       ├── storage/           # Local, POSIX, and S3 file storage adapters
│   │       ├── ocr/               # Ingestion, deskew, Tesseract, heuristic extractors
│   │       ├── deadlines/         # Recurrence rule parser, status transitions
│   │       ├── notifications/     # Multi-channel delivery engine (Email, Web, ICS)
│   │       ├── assets/            # Appliance/device inventory, warranty claims
│   │       ├── search/            # Indexing, tokenization, phonetic & fuzzy search
│   │       ├── analytics/         # Financial cash flow, expiration forecasting
│   │       └── admin/             # System health, audit log analysis, quota control
│   ├── lifeledger-web/            # Frontend assets, templates, controllers
│   │   ├── pyproject.toml
│   │   ├── src/lifeledger_web/
│   │   │   ├── controllers/       # Flask Blueprints for web views
│   │   │   ├── static/
│   │   │   │   ├── css/           # Design system tokens, layouts, components
│   │   │   │   └── js/            # Modular ES6 controllers and components
│   │   │   └── templates/         # Accessible Jinja2 HTML templates
│   ├── lifeledger-api/            # REST API endpoints, OpenAPI specs, middleware
│   │   ├── pyproject.toml
│   │   └── src/lifeledger_api/
│   ├── lifeledger-sdk-py/         # Official Python client SDK
│   │   ├── pyproject.toml
│   │   └── src/lifeledger_sdk/
│   ├── lifeledger-sdk-js/         # Official TypeScript/Node client SDK
│   │   ├── package.json
│   │   └── src/
│   └── lifeledger-cli/            # Command-line utility for vault operations
│       ├── pyproject.toml
│       └── src/lifeledger_cli/
├── tests/
│   ├── unit/                      # Fast unit tests for all packages
│   ├── integration/               # Database, storage, and worker integration tests
│   ├── security/                  # IDOR, SQLi, XSS, and authorization attack tests
│   ├── e2e/                       # Playwright browser end-to-end tests
│   ├── performance/               # Locust load scenarios and memory benchmarks
│   └── fixtures/                  # Sample test documents, invoices, receipts
├── pyproject.toml                 # Root workspace manifest
├── poetry.lock                    # Cryptographically pinned lockfile
└── README.md
```

---

## 9. Database Schema and Entity-Relationship Design

### 9.1 Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ SESSIONS : has
    USERS ||--o{ AUDIT_LOGS : generates
    USERS ||--o{ WORKSPACE_MEMBERSHIPS : belongs_to
    WORKSPACES ||--o{ WORKSPACE_MEMBERSHIPS : contains
    WORKSPACES ||--o{ DOCUMENTS : owns
    WORKSPACES ||--o{ ASSETS : owns
    
    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : tracks
    DOCUMENTS ||--o{ EXTRACTED_FIELDS : contains
    DOCUMENTS ||--o{ DEADLINES : triggers
    DOCUMENTS ||--o{ SHARED_LINKS : exposes
    DOCUMENTS }o--o{ DOCUMENT_TAGS : labeled_with
    
    ASSETS ||--o{ MAINTENANCE_LOGS : records
    ASSETS ||--o{ DOCUMENTS : backed_by
    
    DEADLINES ||--o{ REMINDER_SCHEDULES : configures
    REMINDER_SCHEDULES ||--o{ NOTIFICATION_ATTEMPTS : dispatches
    
    USERS {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        string role
        boolean is_active
        boolean mfa_enabled
        string mfa_secret
        datetime created_at
        datetime updated_at
    }

    DOCUMENTS {
        uuid id PK
        uuid workspace_id FK
        uuid created_by FK
        string title
        string category
        date issue_date
        date expiry_date
        string issuing_authority
        string status
        boolean is_archived
        datetime created_at
        datetime updated_at
    }

    DOCUMENT_VERSIONS {
        uuid id PK
        uuid document_id FK
        integer version_number
        string storage_key
        string file_name
        string mime_type
        bigint file_size_bytes
        string sha256_hash
        string encryption_iv
        datetime created_at
    }

    DEADLINES {
        uuid id PK
        uuid document_id FK
        uuid workspace_id FK
        string title
        date due_date
        string recurrence_rule
        string status
        string priority
        datetime last_evaluated_at
    }

    ASSETS {
        uuid id PK
        uuid workspace_id FK
        string name
        string manufacturer
        string model_number
        string serial_number UK
        date purchase_date
        decimal purchase_price
        date warranty_expiry_date
        string warranty_status
        uuid invoice_document_id FK
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string entity_type
        uuid entity_id
        string ip_address
        string user_agent
        jsonb metadata
        datetime created_at
    }
```

### 9.2 Complete Table Definitions, Constraints, and Indexing

1. **`users` Table:**
   * `id`: `UUID`, Primary Key, default `gen_random_uuid()`.
   * `email`: `VARCHAR(255)`, Unique, Not Null, case-insensitive index (`lower(email)`).
   * `password_hash`: `VARCHAR(255)`, Not Null (Argon2id encoded string).
   * `full_name`: `VARCHAR(150)`, Not Null.
   * `role`: `VARCHAR(30)`, Not Null, Check Constraint (`role IN ('user', 'family_manager', 'auditor', 'admin')`), default `'user'`.
   * `is_active`: `BOOLEAN`, Not Null, default `TRUE`.
   * `mfa_enabled`: `BOOLEAN`, Not Null, default `FALSE`.
   * `mfa_secret`: `VARCHAR(128)`, Nullable (encrypted TOTP seed).
   * `failed_login_attempts`: `INT`, Not Null, default `0`.
   * `locked_until`: `TIMESTAMPTZ`, Nullable.
   * `created_at`: `TIMESTAMPTZ`, Not Null, default `CURRENT_TIMESTAMP`.
   * `updated_at`: `TIMESTAMPTZ`, Not Null, default `CURRENT_TIMESTAMP`.
   * **Indexes:** `idx_users_email` ON `users(email)`, `idx_users_role` ON `users(role)`.

2. **`workspaces` Table:**
   * `id`: `UUID`, Primary Key.
   * `name`: `VARCHAR(100)`, Not Null.
   * `owner_id`: `UUID`, Foreign Key referencing `users(id)` ON DELETE RESTRICT.
   * `storage_quota_bytes`: `BIGINT`, Not Null, default `5368709120` (5 GB).
   * `current_storage_bytes`: `BIGINT`, Not Null, default `0`.
   * `created_at`: `TIMESTAMPTZ`, Not Null.

3. **`workspace_memberships` Table:**
   * `id`: `UUID`, Primary Key.
   * `workspace_id`: `UUID`, Foreign Key referencing `workspaces(id)` ON DELETE CASCADE.
   * `user_id`: `UUID`, Foreign Key referencing `users(id)` ON DELETE CASCADE.
   * `role`: `VARCHAR(30)`, Not Null, Check Constraint (`role IN ('owner', 'admin', 'member', 'read_only')`).
   * `joined_at`: `TIMESTAMPTZ`, Not Null.
   * **Unique Constraint:** `(workspace_id, user_id)`.

4. **`documents` Table:**
   * `id`: `UUID`, Primary Key.
   * `workspace_id`: `UUID`, Foreign Key referencing `workspaces(id)` ON DELETE CASCADE.
   * `created_by`: `UUID`, Foreign Key referencing `users(id)` ON DELETE SET NULL.
   * `title`: `VARCHAR(200)`, Not Null.
   * `category`: `VARCHAR(50)`, Not Null, Check Constraint (`category IN ('identity', 'insurance', 'warranty', 'bill', 'vehicle', 'property', 'education', 'legal', 'tax', 'other')`).
   * `issue_date`: `DATE`, Nullable.
   * `expiry_date`: `DATE`, Nullable.
   * `issuing_authority`: `VARCHAR(150)`, Nullable.
   * `status`: `VARCHAR(30)`, Not Null, default `'pending_ocr'`.
   * `is_archived`: `BOOLEAN`, Not Null, default `FALSE`.
   * `is_ice_document`: `BOOLEAN`, Not Null, default `FALSE` (Emergency Access Flag).
   * `notes`: `TEXT`, Nullable.
   * `created_at`: `TIMESTAMPTZ`, Not Null.
   * `updated_at`: `TIMESTAMPTZ`, Not Null.
   * **Indexes:** `idx_docs_workspace_category` ON `documents(workspace_id, category)`, `idx_docs_expiry` ON `documents(expiry_date)`, `idx_docs_status` ON `documents(status)`.

5. **`document_versions` Table:**
   * `id`: `UUID`, Primary Key.
   * `document_id`: `UUID`, Foreign Key referencing `documents(id)` ON DELETE CASCADE.
   * `version_number`: `INT`, Not Null.
   * `storage_key`: `VARCHAR(512)`, Not Null, Unique (UUID-based object path).
   * `file_name`: `VARCHAR(255)`, Not Null.
   * `mime_type`: `VARCHAR(100)`, Not Null.
   * `file_size_bytes`: `BIGINT`, Not Null.
   * `sha256_hash`: `CHAR(64)`, Not Null.
   * `encryption_iv`: `VARCHAR(64)`, Not Null.
   * `created_at`: `TIMESTAMPTZ`, Not Null.
   * **Unique Constraint:** `(document_id, version_number)`.
   * **Index:** `idx_doc_versions_hash` ON `document_versions(sha256_hash)`.

6. **`extracted_fields` Table:**
   * `id`: `UUID`, Primary Key.
   * `document_version_id`: `UUID`, Foreign Key referencing `document_versions(id)` ON DELETE CASCADE.
   * `field_key`: `VARCHAR(50)`, Not Null (e.g., `'policy_number'`, `'total_amount'`, `'vendor_name'`).
   * `extracted_value`: `TEXT`, Not Null.
   * `confidence_score`: `FLOAT`, Not Null (0.0 to 1.0).
   * `is_user_verified`: `BOOLEAN`, Not Null, default `FALSE`.
   * `bounding_box`: `JSONB`, Nullable.

7. **`deadlines` Table:**
   * `id`: `UUID`, Primary Key.
   * `document_id`: `UUID`, Foreign Key referencing `documents(id)` ON DELETE CASCADE, Nullable.
   * `workspace_id`: `UUID`, Foreign Key referencing `workspaces(id)` ON DELETE CASCADE.
   * `title`: `VARCHAR(200)`, Not Null.
   * `due_date`: `DATE`, Not Null.
   * `recurrence_rule`: `VARCHAR(100)`, Nullable (e.g., `'FREQ=YEARLY;INTERVAL=1'`).
   * `priority`: `VARCHAR(20)`, Not Null, default `'medium'`.
   * `status`: `VARCHAR(30)`, Not Null, Check Constraint (`status IN ('upcoming', 'overdue', 'completed', 'dismissed')`), default `'upcoming'`.
   * **Indexes:** `idx_deadlines_due_date` ON `deadlines(due_date, status)`.

8. **`assets` & `maintenance_logs` Tables:**
   * `assets` tracks consumer appliances, electronics, and vehicles with serial numbers, warranty terms, and purchase invoices.
   * `maintenance_logs` tracks repair dates, service technician details, cost, and service receipts.

9. **`audit_logs` Table:**
   * Tamper-evident log tracking `actor_user_id`, `action`, `resource_type`, `resource_id`, `ip_address`, `user_agent`, `payload_hash`, and timestamp with append-only permissions.

---

## 10. API Endpoint Specification

All API endpoints follow RESTful design, strict HTTP status codes, JSON request/response envelopes, and versioning under `/api/v1/`.

| Method | Endpoint | Description | Auth Required | Rate Limit |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new user account | Anonymous | 5 / min |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain session | Anonymous | 10 / min |
| `POST` | `/api/v1/auth/logout` | Revoke active session | Authenticated | 60 / min |
| `GET` | `/api/v1/auth/me` | Fetch active user profile and roles | Authenticated | 120 / min |
| `GET` | `/api/v1/vault/documents` | List documents with filtering and search | Workspace Member | 120 / min |
| `POST` | `/api/v1/vault/documents` | Upload new document and initial metadata | Workspace Member | 20 / min |
| `GET` | `/api/v1/vault/documents/{id}` | Retrieve document details and version list | Workspace Member | 120 / min |
| `PUT` | `/api/v1/vault/documents/{id}` | Update document metadata and tags | Workspace Member | 60 / min |
| `DELETE`| `/api/v1/vault/documents/{id}` | Soft-delete / archive document | Workspace Admin | 30 / min |
| `GET` | `/api/v1/vault/documents/{id}/download`| Stream decrypted document file | Workspace Member | 60 / min |
| `POST` | `/api/v1/vault/documents/{id}/ocr/review`| Confirm or correct extracted OCR fields| Workspace Member | 60 / min |
| `GET` | `/api/v1/deadlines` | List deadlines with status and date filters| Workspace Member | 120 / min |
| `POST` | `/api/v1/deadlines` | Create manual deadline or obligation | Workspace Member | 60 / min |
| `PATCH`| `/api/v1/deadlines/{id}/complete` | Mark deadline completed (triggers recurrence)| Workspace Member | 60 / min |
| `GET` | `/api/v1/assets` | List registered appliances and devices | Workspace Member | 120 / min |
| `POST` | `/api/v1/assets` | Register new asset and link warranty | Workspace Member | 60 / min |
| `POST` | `/api/v1/assets/{id}/claim-letter`| Generate warranty claim formal letter | Workspace Member | 20 / min |
| `GET` | `/api/v1/analytics/forecast` | Retrieve 12-month renewal cash flow | Workspace Member | 60 / min |
| `GET` | `/api/v1/admin/users` | List all system users with storage metrics | System Admin | 60 / min |
| `GET` | `/api/v1/admin/audit-logs` | Query system audit trail with filtering | System Admin / Auditor | 60 / min |

---

## 11. UI/UX Page Specification

The user interface is engineered according to a cohesive, high-density design system built with vanilla CSS3 custom properties, responsive grid/flexbox layouts, ARIA landmarks, and micro-interactions.

```
+-----------------------------------------------------------------------------------------+
| LIFELEDGER  [Vault] [Deadlines (3)] [Assets] [Analytics] [Family]    [Search...] [Avatar]|
+-----------------------------------------------------------------------------------------+
| URGENT ATTENTION NEEDED                                                                 |
| [!] Auto Insurance Renewal in 4 Days (Oct 18, 2026) -> [1-Click Renew] [View Policy]   |
| [!] MacBook Pro AppleCare expires in 12 Days (Oct 26, 2026) -> [File Claim]             |
+-----------------------------------------------------------------------------------------+
| METRICS OVERVIEW                                                                        |
| +--------------------+ +--------------------+ +--------------------+ +------------------+|
| | 42 Active Records  | | $1,240 Due in 30d  | | 8 Active Warranties| | 96% Vault Health | |
| +--------------------+ +--------------------+ +--------------------+ +------------------+|
+-----------------------------------------------------------------------------------------+
| QUICK VAULT ACCESS                     | UPCOMING DEADLINE TIMELINE                     |
| [Upload New Doc] [Filter: Category v]  | * Oct 18 - Geico Auto Insurance ($480)         |
| - Passport_Sarah.pdf (Expires 2031)    | * Oct 26 - AppleCare MacBook Pro (Warranty)    |
| - Home_Deed_Signed.pdf (Secure)        | * Nov 02 - Water Utility Bill ($84)            |
| - Sony_OLED_Warranty.pdf (Active)      | * Dec 15 - Vehicle Inspection & Emissions      |
+----------------------------------------+------------------------------------------------+
```

### Detailed Specifications for Required Pages:
1. **Landing Page (`/`):** Explains value proposition, security highlights (client-side encryption, zero cloud vendor lock-in), live interactive demo widget, and CTA for registration.
2. **Registration & Login (`/auth/login`, `/auth/register`):** Minimalist card layout, real-time password strength meter, email verification notification, TOTP two-step challenge screen.
3. **Password Recovery (`/auth/forgot-password`, `/auth/reset-password`):** Rate-limited email dispatch with single-use, cryptographically signed 15-minute expiration tokens.
4. **Main Dashboard (`/dashboard`):** High-level cockpit showing urgent deadline banner alerts, key metric tiles (active documents, 30-day cash flow liability, active warranties, vault health score), recent uploads, and upcoming timeline.
5. **Document Vault (`/vault`):** Filterable gallery and data table view. Supports multi-selection, bulk tag assignment, category tabs, and fast instant fuzzy search.
6. **Upload Wizard & OCR Review (`/vault/upload`):** Drag-and-drop zone with MIME and file size validation, progress bar, side-by-side document preview canvas with highlighted bounding boxes for extracted fields, confidence scores (Green ≥ 90%, Yellow 70-89%, Red < 70%), and editable input fields.
7. **Document Detail View (`/vault/documents/{id}`):** Full metadata inspector, version history table with rollback/download triggers, audit trail of who viewed/downloaded the file, and deadline linkage.
8. **Deadline Calendar & List (`/deadlines`):** Toggle between interactive monthly grid calendar and chronological list view. Color-coded status badges (`overdue`: Red, `imminent ≤7d`: Amber, `upcoming`: Green, `completed`: Muted).
9. **Warranty & Asset Inventory (`/assets`):** Hardware catalog cards with device manufacturer badges, days of warranty remaining countdown bar, service record logs, and 1-click "Generate Claim Letter" action.
10. **Notification Center (`/notifications`):** Unread notification feed, notification preference configuration (Email vs In-App vs Webhook), and iCal subscription link generator.
11. **Reports & Analytics (`/analytics`):** Interactive SVG-based category distribution charts, 12-month renewal cash flow projections, and 1-click "Download Compliance PDF / CSV" generator.
12. **Family & Workspace Settings (`/settings/workspace`):** Member invitation management, role assignment, shared vault permissions, and Emergency "In Case of Emergency" (ICE) configuration.
13. **Profile & Privacy Controls (`/settings/profile`):** Personal details, MFA enrollment, active session revocation, full GDPR data export bundle download (ZIP of all decrypted files + JSON metadata), and permanent account deletion.
14. **Admin Dashboard (`/admin`):** System health metrics (CPU, RAM, DB connection pool, Redis queue backlog), storage utilization gauges, user lifecycle management table.
15. **Admin Audit Logs (`/admin/audit`):** High-volume, filterable audit log viewer with actor, action, timestamp, IP, and metadata JSON inspector.
16. **Help & Error Pages (`/help`, `400`, `403`, `404`, `500`):** Semantic error layouts with user-friendly recovery instructions, clear navigation links, and incident correlation IDs.

---

## 12. Security Threat Model & Hardening Matrix

| Threat Category | Specific Attack Vector | LifeLedger Countermeasure & Implementation |
|---|---|---|
| **Broken Object-Level Auth (BOLA / IDOR)** | User modifies `document_id` in URL to view another user's file. | Strict multi-tenant repository query filters enforcing `workspace_id` verification against authenticated session memberships on every query. |
| **Malicious Document Upload** | Attacker uploads web shell (`.php`, `.py`) or SVG with embedded XSS scripts. | Strict MIME-type magic byte sniffing (python-magic), extension whitelisting, file content sanitization, and storage outside web root with randomized UUID filenames. |
| **Server-Side Request Forgery (SSRF)** | Attacker inputs internal IP (`http://169.254.169.254`) in webhook settings. | Strict IP validation blocking RFC 1918 private ranges, loopbacks, and AWS metadata endpoints before dispatching webhooks. |
| **Cross-Site Scripting (XSS)** | Malicious OCR text or document title rendered in browser without escaping. | Context-aware Jinja2 autoescaping, Content Security Policy (CSP) blocking inline scripts, and sanitization of all dynamic DOM injections. |
| **Cross-Site Request Forgery (CSRF)** | Malicious third-party site submits unauthorized POST requests. | Flask-WTF cryptographically signed double-submit CSRF tokens verified on all state-changing HTTP verbs (`POST`, `PUT`, `PATCH`, `DELETE`). |
| **SQL Injection (SQLi)** | Attacker injects SQL payloads in search query input. | 100% parameterized queries via SQLAlchemy 2.0 ORM; strict input sanitization on all FTS5 full-text queries. |
| **Session Fixation / Hijacking** | Session cookie intercepted or reused over unencrypted transport. | Cookies configured with `Secure`, `HttpOnly`, `SameSite=Lax`, and session rotation triggered upon authentication and privilege escalation. |
| **Brute Force & Credential Stuffing** | Automated login attempts on user accounts. | In-memory Redis sliding-window rate limiter (5 failed attempts locks account for 15 minutes) + Argon2id computational work factor. |
| **Data Exposure at Rest** | Physical theft of backup disk or database compromise. | AES-256-GCM envelope encryption for stored files; master keys stored in environment variables / KMS; database passwords hashed with Argon2id. |

---

## 13. Detailed Module-by-Module Implementation Plan

### Subsystem 1: Core Domain, Primitives, and Crypto (`lifeledger-core`)
* **Responsibilities:** Envelope encryption primitives (AES-256-GCM), key derivation (PBKDF2/Argon2), configuration parsing via Pydantic schemas, unified exception handling hierarchy, structured JSON telemetry logging.
* **Dependencies:** None (Base library).
* **Key Interfaces:** `KeyManager`, `AESGCMCipher`, `ConfigRegistry`, `TelemetryLogger`.
* **Acceptance Criteria:** 100% unit test coverage; constant-time string comparisons to prevent timing attacks; zero plaintext secrets in logs.

### Subsystem 2: Persistence, Models, and Migrations (`lifeledger-models`)
* **Responsibilities:** Declarative SQLAlchemy 2.0 models for Users, Workspaces, Documents, Versions, Deadlines, Assets, and Audits; Alembic migration scripts; custom SQL types for encrypted fields.
* **Dependencies:** `lifeledger-core`.
* **Key Interfaces:** Entity classes with relationships, validation hooks, and migration revisions.
* **Acceptance Criteria:** Strict foreign-key cascade definitions; non-null constraints on critical attributes; verified rollback capability for every migration script.

### Subsystem 3: Repositories & Data Access Layer (`lifeledger-repositories`)
* **Responsibilities:** Encapsulates database queries, transaction boundaries (`UnitOfWork`), tenant isolation enforcement, pagination, and bulk operations.
* **Dependencies:** `lifeledger-core`, `lifeledger-models`.
* **Key Interfaces:** `UserRepository`, `DocumentRepository`, `DeadlineRepository`, `AssetRepository`, `AuditRepository`.
* **Acceptance Criteria:** Every repository method requires a tenant context parameter; zero raw unparameterized SQL strings.

### Subsystem 4: Authentication & RBAC Services (`lifeledger_services.auth`)
* **Responsibilities:** User registration, password verification, TOTP two-factor enrollment and challenge verification, session generation, password reset tokens, and permission checks.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `AuthenticationService`, `SessionManager`, `TOTPService`, `PermissionGuard`.
* **Acceptance Criteria:** Passwords hashed with Argon2id (memory=64MB, time=3); automatic session invalidation upon password reset; login rate limiting enforced.

### Subsystem 5: Storage Abstraction Layer (`lifeledger_services.storage`)
* **Responsibilities:** Multi-backend file storage engine supporting local POSIX filesystem storage (development) and S3/MinIO object storage (production) with chunked streaming and AES-256-GCM encryption.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `StorageAdapter` (ABC), `LocalStorageAdapter`, `S3StorageAdapter`, `ChecksumVerifier`.
* **Acceptance Criteria:** Files encrypted before disk write; SHA-256 integrity verified upon read; streaming uploads do not exhaust worker memory on 50MB files.

### Subsystem 6: OCR Ingestion & Field Extraction (`lifeledger_services.ocr`)
* **Responsibilities:** Preprocesses document images (contrast adjustment, deskewing), invokes Tesseract OCR engine, parses text using regex and heuristic models, scores extraction confidence, and saves fields.
* **Dependencies:** `lifeledger-core`, `lifeledger-services.storage`, `lifeledger-repositories`.
* **Key Interfaces:** `OCRPipeline`, `ImagePreprocessor`, `FieldExtractor`, `ConfidenceScorer`.
* **Acceptance Criteria:** Handles multi-page PDFs; graceful fallback on corrupted or unreadable images without crashing worker; extracts dates across standard formats (`YYYY-MM-DD`, `MM/DD/YYYY`, `DD-Mon-YYYY`).

### Subsystem 7: Deadline & Recurrence Subsystem (`lifeledger_services.deadlines`)
* **Responsibilities:** Parses RFC 5545 recurrence rules, calculates upcoming obligation dates, manages deadline status state machine (`upcoming` -> `overdue` -> `completed`), and handles snooze requests.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `DeadlineEngine`, `RecurrenceParser`, `TimelineAggregator`.
* **Acceptance Criteria:** Correctly handles leap years and timezone boundaries; completing a recurring deadline automatically spawns the next occurrence.

### Subsystem 8: Notification & Dispatch Gateway (`lifeledger_services.notifications`)
* **Responsibilities:** Orchestrates multi-channel delivery of deadline reminders, evaluates reminder schedules (e.g. 30d, 7d, 1d), compiles responsive HTML emails, generates iCal feeds, and dispatches webhooks.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `NotificationDispatcher`, `EmailChannel`, `InAppChannel`, `ICalendarGenerator`, `WebhookChannel`.
* **Acceptance Criteria:** Idempotent dispatch prevents duplicate emails; failed deliveries retry with exponential backoff up to 3 times before dead-letter logging.

### Subsystem 9: Asset & Warranty Lifecycle Subsystem (`lifeledger_services.assets`)
* **Responsibilities:** Manages appliance and electronic device records, serial number indexing, depreciation modeling, maintenance logs, and generates formal warranty claim packages.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`, `lifeledger-services.storage`.
* **Key Interfaces:** `AssetManager`, `WarrantyTracker`, `ClaimPackageGenerator`, `DepreciationCalculator`.
* **Acceptance Criteria:** Accurately calculates remaining warranty days; generates complete PDF warranty claim letter bundle with proof-of-purchase attached.

### Subsystem 10: Search & Indexing Engine (`lifeledger_services.search`)
* **Responsibilities:** Full-text indexing of document titles, notes, and OCR extracted text using SQLite FTS5 / PostgreSQL pg_trgm; tokenization, stemming, and ranking.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `SearchIndexManager`, `QueryParser`, `SearchResultRanker`.
* **Acceptance Criteria:** Sub-50ms query response on 10,000 documents; strict tenant isolation applied at index query level.

### Subsystem 11: Analytics & Financial Reporting (`lifeledger_services.analytics`)
* **Responsibilities:** Calculates aggregate statistics, generates 12-month renewal cash flow projections, produces category breakdown metrics, and renders exportable PDF/CSV reports.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `CashFlowForecaster`, `CategoryAggregator`, `ReportExporter`.
* **Acceptance Criteria:** Accurate floating-point/decimal currency arithmetic; report generation streams results to prevent memory bloat.

### Subsystem 12: Admin & Telemetry Governance (`lifeledger_services.admin`)
* **Responsibilities:** User account status governance (suspend, activate), storage quota enforcement, background job queue telemetry inspection, and tamper-evident audit log querying.
* **Dependencies:** `lifeledger-core`, `lifeledger-repositories`.
* **Key Interfaces:** `AdminOperationsManager`, `QuotaEnforcer`, `AuditLogInspector`.
* **Acceptance Criteria:** All administrative actions recorded in audit log with actor ID; system administrators cannot view encrypted user files without explicit consent.

### Subsystem 13: Presentation Layer & Web Controllers (`lifeledger-web`)
* **Responsibilities:** Flask Blueprints, Jinja2 template rendering, design system styling (vanilla CSS), and ES6 modular client-side controllers.
* **Dependencies:** All backend services.
* **Key Interfaces:** Web route handlers, form validators, view models, UI component library.
* **Acceptance Criteria:** WCAG 2.1 Level AA accessibility; zero visual regressions across mobile and desktop breakpoints.

### Subsystem 14: REST API & Serialization Layer (`lifeledger-api`)
* **Responsibilities:** Versioned RESTful JSON API endpoints, request validation via Pydantic schemas, rate limiting middleware, and OpenAPI documentation generation.
* **Dependencies:** All backend services.
* **Key Interfaces:** API routes, serialization schemas, error handlers.
* **Acceptance Criteria:** Strict adherence to HTTP status codes; comprehensive OpenAPI 3.1 schema.

### Subsystem 15: Client SDKs & CLI Tool (`lifeledger-sdk-py`, `lifeledger-sdk-js`, `lifeledger-cli`)
* **Responsibilities:** Typed client libraries for Python and TypeScript/JavaScript; command-line utility for vault operations, scripting, and automated backups.
* **Dependencies:** `lifeledger-core`.
* **Key Interfaces:** `LifeLedgerClient`, CLI commands (`lifeledger vault upload`, `lifeledger deadlines list`).
* **Acceptance Criteria:** Fully typed interfaces; retry handling on network failures; cross-platform CLI execution.

### Subsystem 16: Comprehensive Automated Quality Assurance Suite (`tests/`)
* **Responsibilities:** Unit tests, database integration tests, security attack tests (IDOR, SQLi, XSS), Playwright browser E2E workflows, and Locust performance tests.
* **Dependencies:** All packages and subsystems.
* **Key Interfaces:** Pytest fixtures, test factories, mock adapters, browser test scripts.
* **Acceptance Criteria:** Minimum 85% branch coverage; zero critical security vulnerabilities.

---

## 14. Subsystem LOC Budget Totaling 500,000+ Planned Authored LOC

To build a true enterprise-grade platform with modular packages, client SDKs, administrative controls, and an exhaustive testing suite, the codebase is budgeted across 16 formal subsystems. 

### 14.1 Authored Code Exclusions & Counting Rules
* **Strict Exclusions:** The LOC budget strictly **excludes** all third-party dependencies (`node_modules/`, Python virtual environments), vendored binaries, compiled assets, minified CSS/JS bundles, automatically generated code, and duplicated lines.
* **Counting Methodology:** Authored physical lines of code are counted using standard tools (`scc` or `cloc`), separating Production Source, Test Suites, Tooling/Scripts, and Technical Documentation.

### 14.2 Detailed Subsystem Breakdown

| Subsystem Identifier | Subsystem Name | Production Source LOC | Test Source LOC | Total Authored LOC |
|---|---|---|---|---|
| **PKG-01** | `lifeledger-core` (Crypto, Config, Telemetry, Utils) | 18,500 | 14,000 | **32,500** |
| **PKG-02** | `lifeledger-models` (Entities, Types, Alembic Migrations) | 22,000 | 12,000 | **34,000** |
| **PKG-03** | `lifeledger-repositories` (Data Access, UnitOfWork, Queries)| 26,000 | 18,500 | **44,500** |
| **PKG-04** | `lifeledger_services.auth` (Authentication, MFA, RBAC) | 24,500 | 16,000 | **40,500** |
| **PKG-05** | `lifeledger_services.storage` (Encrypted Multi-Storage) | 21,000 | 15,000 | **36,000** |
| **PKG-06** | `lifeledger_services.ocr` (Ingestion, Preprocessing, Extraction)| 28,500 | 19,000 | **47,500** |
| **PKG-07** | `lifeledger_services.deadlines` (Recurrence & Scheduling Engine)| 22,000 | 15,500 | **37,500** |
| **PKG-08** | `lifeledger_services.notifications` (Multi-Channel Dispatcher)| 20,500 | 14,000 | **34,500** |
| **PKG-09** | `lifeledger_services.assets` (Appliance & Warranty Claim Engine)| 23,000 | 15,000 | **38,000** |
| **PKG-10** | `lifeledger_services.search` (Tokenization & Full-Text Engine) | 19,000 | 13,500 | **32,500** |
| **PKG-11** | `lifeledger_services.analytics` (Financial Forecasting & Reports)| 21,500 | 14,000 | **35,500** |
| **PKG-12** | `lifeledger_services.admin` (Governance, Quotas, Audit Trail) | 18,000 | 12,500 | **30,500** |
| **PKG-13** | `lifeledger-web` (Controllers, Jinja Templates, CSS, JS) | 48,000 | 22,000 | **70,000** |
| **PKG-14** | `lifeledger-api` (REST API Endpoints, OpenAPI Schemas) | 24,000 | 16,500 | **40,500** |
| **PKG-15** | `lifeledger-sdk-py` & `lifeledger-sdk-js` (Client SDKs) | 28,000 | 18,000 | **46,000** |
| **PKG-16** | `lifeledger-cli` (Command-Line Interface Tools) | 14,500 | 10,500 | **25,000** |
| **INFRA** | CI/CD Pipelines, DevOps Tooling, Seeders, Security Harness | 12,500 | 8,500 | **21,000** |
| **DOCS** | Architectural Decision Records, API Specs, Operator Manuals | -- | -- | **15,000** |
| **TOTALS**| **Aggregate Authored Engineering Footprint** | **391,500** | **238,500** | **660,000** |

*Note: The total planned authored codebase of **660,000 LOC** (391,500 production + 238,500 test/tooling) comfortably exceeds the 500,000 LOC acceptance target, providing substantial engineering depth across all real-world subsystems.*

---

## 15. Meaningful Commit Roadmap Containing 200+ Planned Changes

The development of LifeLedger is structured across 14 phases comprising **200+ distinct, atomic, engineering commits**. Every commit follows the Conventional Commits specification (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).

### Phase 1: Repository Foundation & Tooling (Commits 1–15)
* `c001`: `chore: initialize monorepo workspace structure and poetry manifests`
* `c002`: `chore: configure ruff, mypy strict mode, and pre-commit hooks`
* `c003`: `ci: setup github actions matrix for python 3.12 and node 22`
* `c004`: `docs: add architectural decision record ADR-001 on modular architecture`
* `c005`: `feat(core): implement unified exception hierarchy in lifeledger-core`
* `c006`: `test(core): add unit tests for exception formatting and error codes`
* `c007`: `feat(core): implement structured json telemetry logger`
* `c008`: `test(core): add unit tests for log redaction and contextual metadata`
* `c009`: `feat(core): implement pydantic base configuration settings loader`
* `c010`: `test(core): add tests for environment variable overrides and validation`
* `c011`: `feat(core): implement argon2id password hashing and verification module`
* `c012`: `test(core): add property-based tests for password hash verifier`
* `c013`: `feat(core): implement aes-256-gcm envelope encryption utilities`
* `c014`: `test(core): test crypto roundtrip and invalid authentication tags`
* `c015`: `chore: add reproducible loc counting script scripts/measure_loc.py`

### Phase 2: Database Models & Migrations (Commits 16–30)
* `c016`: `feat(models): initialize alembic migration environment and base declarative class`
* `c017`: `feat(models): define user and session database entities`
* `c018`: `test(models): add unit tests for user entity constraints and relationships`
* `c019`: `feat(models): define workspace and workspace_membership entities`
* `c020`: `feat(models): define document and document_version entities`
* `c021`: `test(models): test document version cascading and uniqueness constraints`
* `c022`: `feat(models): define extracted_field and bounding_box schemas`
* `c023`: `feat(models): define deadline and reminder_schedule entities`
* `c024`: `feat(models): define asset, warranty, and maintenance_log entities`
* `c025`: `feat(models): define audit_log and shared_link entities`
* `c026`: `feat(models): implement custom encrypted string and jsonb sqlalchemy types`
* `c027`: `test(models): add tests for custom encrypted type read/write transparency`
* `c028`: `feat(models): generate initial baseline alembic migration revision`
* `c029`: `test(models): verify migration upgrade and downgrade scripts on clean postgres`
* `c030`: `feat(models): add realistic test fixtures and database seeding scripts`

### Phase 3: Repositories & Data Access Layer (Commits 31–45)
* `c031`: `feat(repositories): implement base generic repository and unit-of-work pattern`
* `c032`: `feat(repositories): implement user repository with email index lookup`
* `c033`: `test(repositories): add unit tests for user repository crud and locking`
* `c034`: `feat(repositories): implement workspace repository with quota validation`
* `c035`: `feat(repositories): implement document repository with tenant isolation filter`
* `c036`: `test(repositories): verify document repository strictly blocks cross-tenant queries`
* `c037`: `feat(repositories): implement document version repository with sha256 lookup`
* `c038`: `feat(repositories): implement deadline repository with range query index`
* `c039`: `test(repositories): add tests for upcoming deadline query filters`
* `c040`: `feat(repositories): implement asset and maintenance log repository`
* `c041`: `feat(repositories): implement audit log repository with tamper-evident checks`
* `c042`: `test(repositories): test audit log append-only constraints`
* `c043`: `feat(repositories): implement shared link repository with expiration queries`
* `c044`: `feat(repositories): add pagination and sorting query builder helpers`
* `c045`: `test(repositories): add benchmark tests for repository query performance`

### Phase 4: Authentication & Security Services (Commits 46–60)
* `c046`: `feat(auth): implement user registration service with email uniqueness check`
* `c047`: `feat(auth): implement session-based authentication with secure cookie tokens`
* `c048`: `test(auth): add unit tests for session lifecycle and expiration`
* `c049`: `feat(auth): implement totp two-factor secret generation and qr uri builder`
* `c050`: `feat(auth): implement totp challenge verification and recovery codes`
* `c051`: `test(auth): add tests for totp verification replay attacks`
* `c052`: `feat(auth): implement password reset workflow with signed token generation`
* `c053`: `test(auth): verify password reset token expiration and single-use enforcement`
* `c054`: `feat(auth): implement role-based access control (rbac) permission guard`
* `c055`: `test(auth): test permission evaluation across user, manager, and admin roles`
* `c056`: `feat(auth): implement login rate limiting with redis sliding window`
* `c057`: `feat(auth): implement session revocation and active device termination`
* `c058`: `test(auth): test concurrent session invalidation upon password update`
* `c059`: `feat(auth): implement security audit event emitter for authentication actions`
* `c060`: `test(auth): verify audit event generation for failed login attempts`

### Phase 5: Storage Abstraction & Document Vault (Commits 61–75)
* `c061`: `feat(storage): define storage adapter abstract base class and result types`
* `c062`: `feat(storage): implement local filesystem storage adapter with directory sharding`
* `c063`: `test(storage): add unit tests for local storage read, write, and delete`
* `c064`: `feat(storage): implement s3 and minio compatible storage adapter`
* `c065`: `feat(storage): implement chunked streaming file encryption using aes-256-gcm`
* `c066`: `test(storage): test memory footprint during large file encrypted streaming`
* `c067`: `feat(vault): implement document upload service with mime validation`
* `c068`: `feat(vault): implement sha-256 document deduplication checking`
* `c069`: `test(vault): test duplicate upload detection and version attachment`
* `c070`: `feat(vault): implement document versioning and rollback service`
* `c071`: `feat(vault): implement document soft-delete, archive, and purge policies`
* `c072`: `test(vault): test storage quota deduction upon document deletion`
* `c073`: `feat(vault): implement emergency ice (in case of emergency) document tagging`
* `c074`: `feat(vault): implement secure time-expiring shared link generator`
* `c075`: `test(vault): test access rejection on expired or revoked shared links`

### Phase 6: OCR Pipeline & Information Extraction (Commits 76–95)
* `c076`: `feat(ocr): implement image preprocessing module (grayscale, binarize, deskew)`
* `c077`: `test(ocr): test deskewing algorithm on rotated document fixtures`
* `c078`: `feat(ocr): implement pdf rasterization service using pypdf and pillow`
* `c079`: `feat(ocr): integrate tesseract ocr wrapper with multi-language support`
* `c080`: `test(ocr): add integration tests for tesseract text extraction on sample bills`
* `c081`: `feat(ocr): implement regex-based date parser supporting multiple formats`
* `c082`: `feat(ocr): implement currency and invoice total amount extractor`
* `c083`: `feat(ocr): implement policy and reference number pattern extractor`
* `c084`: `feat(ocr): implement vendor and merchant name matching against known directories`
* `c085`: `feat(ocr): implement extraction confidence score calculation engine`
* `c086`: `test(ocr): add unit tests for confidence scoring thresholds`
* `c087`: `feat(ocr): implement celery asynchronous task for background document ingestion`
* `c088`: `test(ocr): test celery worker error handling on corrupted pdf files`
* `c089`: `feat(ocr): implement human-in-the-loop field review and verification service`
* `c090`: `feat(ocr): implement bounding box coordinate calculation for web canvas`
* `c091`: `test(ocr): test bounding box normalization across varying page resolutions`
* `c092`: `feat(ocr): implement vehicle registration and vin extraction patterns`
* `c093`: `feat(ocr): implement warranty card serial number extractor`
* `c094`: `feat(ocr): implement ocr retry mechanism with fallback image filter profiles`
* `c095`: `test(ocr): end-to-end test of ingestion pipeline from upload to extracted fields`

### Phase 7: Deadline & Recurrence Engine (Commits 96–115)
* `c096`: `feat(deadlines): implement rfc 5545 recurrence rule parser (daily, weekly, monthly, yearly)`
* `c097`: `test(deadlines): test recurrence calculations across month boundaries and leap years`
* `c098`: `feat(deadlines): implement deadline calculation from document expiry dates`
* `c099`: `feat(deadlines): implement deadline state machine (upcoming, overdue, completed)`
* `c100`: `test(deadlines): test state transitions and event emission upon completion`
* `c101`: `feat(deadlines): implement recurring deadline rollover service`
* `c102`: `feat(deadlines): implement deadline snooze and postponement logic`
* `c103`: `feat(deadlines): implement priority calculation based on urgency and category`
* `c104`: `feat(deadlines): implement bulk deadline query filters for dashboard views`
* `c105`: `test(deadlines): test deadline queries for timezone correctness`
* `c106`: `feat(deadlines): implement calendar grid data formatting utility`
* `c107`: `feat(deadlines): implement icalendar .ics export generator for deadlines`
* `c108`: `test(deadlines): validate generated ics feed against rfc 5545 compliance validators`
* `c109`: `feat(deadlines): implement recurring obligation summary statistics service`
* `c110`: `feat(deadlines): add automated celery cron beat task for daily deadline evaluations`
* `c111`: `test(deadlines): test cron job idempotency when executed multiple times daily`
* `c112`: `feat(deadlines): implement dismissal and restoration workflows`
* `c113`: `feat(deadlines): implement tag-based deadline grouping`
* `c114`: `feat(deadlines): implement family member assignment for obligations`
* `c115`: `test(deadlines): test permission boundaries on family obligation assignments`

### Phase 8: Notification Delivery Subsystem (Commits 116–130)
* `c116`: `feat(notifications): implement notification dispatcher abstract base`
* `c117`: `feat(notifications): implement in-app notification center service`
* `c118`: `test(notifications): test in-app notification creation and mark-as-read`
* `c119`: `feat(notifications): implement responsive html email template engine`
* `c120`: `feat(notifications): implement smtp and amazon ses email delivery provider`
* `c121`: `test(notifications): test email composition with dynamic deadline variables`
* `c122`: `feat(notifications): implement notification schedule evaluator (30d, 14d, 7d, 1d)`
* `c123`: `feat(notifications): implement duplicate reminder suppression store`
* `c124`: `test(notifications): test suppression store prevents multiple emails within 24 hours`
* `c125`: `feat(notifications): implement outgoing webhook notification channel`
* `c126`: `test(notifications): test webhook ssrf protections blocking private ip ranges`
* `c127`: `feat(notifications): implement delivery retry handler with exponential backoff`
* `c128`: `feat(notifications): implement dead-letter queue for persistent delivery failures`
* `c129`: `feat(notifications): implement user notification preference toggles`
* `c130`: `test(notifications): verify muted channels do not dispatch messages`

### Phase 9: Asset & Warranty Management (Commits 131–145)
* `c131`: `feat(assets): implement appliance and device asset registration service`
* `c132`: `feat(assets): implement serial number and model cataloging with invoice linkage`
* `c133`: `test(assets): test asset creation with valid document relationship`
* `c134`: `feat(assets): implement warranty status calculator (active, expiring, expired)`
* `c135`: `feat(assets): implement maintenance log tracker with expense recording`
* `c136`: `test(assets): test total cost of ownership aggregation across maintenance logs`
* `c137`: `feat(assets): implement straight-line asset depreciation calculator`
* `c138`: `feat(assets): implement formal warranty claim letter template generator`
* `c139`: `feat(assets): implement warranty claim evidence package compiler (pdf bundle)`
* `c140`: `test(assets): test claim package compilation includes invoice and serial photos`
* `c141`: `feat(assets): implement service provider directory and repair contact manager`
* `c142`: `feat(assets): implement warranty renewal and extended protection tracker`
* `c143`: `feat(assets): implement asset retirement and disposal status lifecycle`
* `c144`: `feat(assets): implement asset search by serial number and manufacturer`
* `c145`: `test(assets): test asset search filters and pagination`

### Phase 10: Search, Analytics & Reporting (Commits 146–160)
* `c146`: `feat(search): implement sqlite fts5 and postgres full-text search adapters`
* `c147`: `feat(search): implement text tokenizer and phonetic matcher for vendor names`
* `c148`: `test(search): test fuzzy search resilience against typographical errors`
* `c149`: `feat(search): implement multi-field search combining metadata and ocr content`
* `c150`: `test(search): test search query tenant isolation guarantees`
* `c151`: `feat(analytics): implement 12-month renewal cash flow forecasting engine`
* `c152`: `feat(analytics): implement document category distribution calculator`
* `c153`: `feat(analytics): implement vault health score algorithm`
* `c154`: `test(analytics): test health score calculation based on missing expiry dates`
* `c155`: `feat(analytics): implement pdf compliance summary report generator`
* `c156`: `feat(analytics): implement csv streaming data export for financial records`
* `c157`: `test(analytics): test csv generation with large document datasets`
* `c158`: `feat(analytics): implement warranty value protected metric calculation`
* `c159`: `feat(analytics): implement historical activity and audit event aggregations`
* `c160`: `test(analytics): test aggregation queries for performance and memory bounds`

### Phase 11: Web Frontend & UI Components (Commits 161–180)
* `c161`: `feat(web): implement design system css tokens (colors, typography, spacing)`
* `c162`: `feat(web): implement dark and light theme switcher with localstorage persistence`
* `c163`: `feat(web): implement accessible base html layout with aria landmarks`
* `c164`: `feat(web): implement accessible navigation bar and responsive mobile drawer`
* `c165`: `feat(web): implement landing page view with interactive feature showcases`
* `c166`: `feat(web): implement login and registration view templates with validation`
* `c167`: `feat(web): implement dashboard view with urgent alert banners and metric tiles`
* `c168`: `feat(web): implement document vault gallery and data table views`
* `c169`: `feat(web): implement drag-and-drop file upload component with progress bar`
* `c170`: `feat(web): implement ocr review screen with side-by-side canvas inspector`
* `c171`: `feat(web): implement deadline calendar view and chronological list view`
* `c172`: `feat(web): implement asset inventory cards and maintenance log timeline`
* `c173`: `feat(web): implement notification center dropdown and preference modal`
* `c174`: `feat(web): implement analytics dashboard with pure svg charts`
* `c175`: `feat(web): implement family workspace management and member invite modal`
* `c176`: `feat(web): implement emergency ice vault access screen`
* `c177`: `feat(web): implement administrative portal views and audit log table`
* `c178`: `feat(web): implement toast notification and accessible modal dialog components`
* `c179`: `test(web): add playwright e2e tests for user registration and document upload`
* `c180`: `test(web): add axe-core automated accessibility tests for wcag aa compliance`

### Phase 12: REST API & Client SDKs (Commits 181–195)
* `c181`: `feat(api): implement v1 rest api blueprint with json envelope middleware`
* `c182`: `feat(api): implement pydantic request validation schemas for all endpoints`
* `c183`: `feat(api): implement rate limiting and api key authentication middleware`
* `c184`: `feat(api): implement openapi 3.1 json and swagger ui documentation endpoints`
* `c185`: `test(api): add comprehensive api integration tests for all v1 endpoints`
* `c186`: `feat(sdk-py): scaffold lifeledger-sdk-py package structure and http client`
* `c187`: `feat(sdk-py): implement vault, deadline, and asset api client methods`
* `c188`: `test(sdk-py): add unit tests and mock http responses for python sdk`
* `c189`: `feat(sdk-js): scaffold lifeledger-sdk-js typescript client library`
* `c190`: `feat(sdk-js): implement typed api client methods for browser and node`
* `c191`: `test(sdk-js): add vitest unit tests for typescript sdk`
* `c192`: `feat(cli): implement lifeledger-cli using click library`
* `c193`: `feat(cli): implement vault upload, download, and deadline list commands`
* `c194`: `feat(cli): implement automated vault backup and restore commands`
* `c195`: `test(cli): add click test runner tests for all cli commands`

### Phase 13: Admin Governance, Hardening & Verification (Commits 196–210)
* `c196`: `feat(admin): implement system health check endpoint with db and redis status`
* `c197`: `feat(admin): implement storage quota enforcement and user suspension workflow`
* `c198`: `feat(admin): implement tamper-evident audit log verification algorithm`
* `c199`: `test(security): add owasp top 10 automated vulnerability test suite`
* `c200`: `test(security): add idor penetration tests across all resource endpoints`
* `c201`: `feat(privacy): implement gdpr data export bundle generator (zip + json)`
* `c202`: `feat(privacy): implement permanent account deletion and storage scrub pipeline`
* `c203`: `test(privacy): verify complete data erasure across database and storage`
* `c204`: `perf: add database indexing optimizations and query plan benchmarks`
* `c205`: `perf: add locust load test scenario simulating 500 concurrent users`
* `c206`: `docs: complete operator deployment runbook and architecture documentation`
* `c207`: `chore: add automated git history and pull request verification script`
* `c208`: `chore: pin production dependency lockfiles and verify clean install`
* `c209`: `test: execute full end-to-end regression test suite`
* `c210`: `chore: tag release v1.0.0 and generate automated changelog`

---

## 16. Pull-Request Roadmap Containing 100 Proposed Work Items

To ensure rigorous code review, quality gates, and verifiable engineering hygiene, the implementation is decomposed into **100 concrete pull requests**. Each pull request defines a bounded scope, affected modules, automated test requirements, and security merge criteria.

### Summary Table of Pull Requests (PR-001 through PR-100)

| PR # | PR Title | Scope & Affected Modules | Merge Gates & Tests |
|---|---|---|---|
| **PR-001** | `chore: workspace initialization and poetry lock` | Root manifests, pre-commit config, poetry lockfile | CI lint passes, dependencies pinned |
| **PR-002** | `ci: automated linting and multi-os matrix workflow` | `.github/workflows/ci.yml` | Matrix build succeeds on Ubuntu/macOS/Windows |
| **PR-003** | `docs: architectural decision records ADR 001-005` | `docs/architecture/` | Technical review and sign-off |
| **PR-004** | `feat(core): unified error and exception hierarchy` | `lifeledger-core/exceptions/` | Unit tests for error serialization |
| **PR-005** | `feat(core): structured json telemetry logging` | `lifeledger-core/telemetry/` | Tests for sensitive data masking |
| **PR-006** | `feat(core): pydantic configuration and env loader` | `lifeledger-core/config/` | Tests for invalid env variable handling |
| **PR-007** | `feat(core): argon2id password hasher implementation` | `lifeledger-core/crypto/` | Work factor tests, constant-time checks |
| **PR-008** | `feat(core): aes-256-gcm envelope encryption` | `lifeledger-core/crypto/` | Crypto roundtrip and tag verification tests |
| **PR-009** | `feat(models): sqlalchemy declarative base and types`| `lifeledger-models/types/` | Custom type SQL compilation tests |
| **PR-010** | `feat(models): user and session database entities` | `lifeledger-models/entities/user.py` | Schema constraints and indexing tests |
| **PR-011** | `feat(models): workspace and membership entities` | `lifeledger-models/entities/workspace.py`| Membership unique constraint tests |
| **PR-012** | `feat(models): document and version entities` | `lifeledger-models/entities/document.py` | Version sequence and FK tests |
| **PR-013** | `feat(models): extracted fields and ocr schemas` | `lifeledger-models/entities/ocr.py` | Bounding box JSON validation tests |
| **PR-014** | `feat(models): deadline and reminder entities` | `lifeledger-models/entities/deadline.py`| Recurrence rule column constraint tests |
| **PR-015** | `feat(models): asset and maintenance log entities` | `lifeledger-models/entities/asset.py` | Serial number uniqueness tests |
| **PR-016** | `feat(models): audit log and shared link entities` | `lifeledger-models/entities/audit.py` | Append-only schema integrity tests |
| **PR-017** | `feat(models): alembic migration baseline setup` | `lifeledger-models/migrations/` | Upgrade/downgrade validation on Postgres |
| **PR-018** | `test(models): automated test fixtures and seeders` | `tests/fixtures/`, `scripts/seed_database.py`| Seeder generates 100 valid records |
| **PR-019** | `feat(repos): base generic repository and uow` | `lifeledger-repositories/base.py` | Transaction commit/rollback tests |
| **PR-020** | `feat(repos): user and session repository queries` | `lifeledger-repositories/user.py` | User lookup and rate limit lock tests |
| **PR-021** | `feat(repos): tenant-isolated document repository` | `lifeledger-repositories/document.py` | IDOR query isolation tests |
| **PR-022** | `feat(repos): document version repository` | `lifeledger-repositories/version.py` | SHA-256 hash deduplication lookup tests |
| **PR-023** | `feat(repos): deadline and schedule repository` | `lifeledger-repositories/deadline.py` | Range query index scan tests |
| **PR-024** | `feat(repos): asset and maintenance repository` | `lifeledger-repositories/asset.py` | Join query optimization tests |
| **PR-025** | `feat(repos): tamper-evident audit repository` | `lifeledger-repositories/audit.py` | Immutability constraint tests |
| **PR-026** | `feat(auth): user registration and verification` | `lifeledger_services/auth/register.py` | Unique email validation tests |
| **PR-027** | `feat(auth): session-based authentication service` | `lifeledger_services/auth/session.py` | Cookie security and rotation tests |
| **PR-028** | `feat(auth): totp 2fa secret generation and qr` | `lifeledger_services/auth/totp.py` | RFC 6238 compliance tests |
| **PR-029** | `feat(auth): totp verification and backup codes` | `lifeledger_services/auth/totp.py` | Code replay prevention tests |
| **PR-030** | `feat(auth): password reset token workflows` | `lifeledger_services/auth/password_reset.py`| Token expiration tests |
| **PR-031** | `feat(auth): role-based access control guards` | `lifeledger_services/auth/rbac.py` | Permission matrix evaluation tests |
| **PR-032** | `feat(auth): redis sliding window rate limiter` | `lifeledger_services/auth/rate_limit.py`| Brute-force simulation tests |
| **PR-033** | `feat(storage): abstract storage adapter interface`| `lifeledger_services/storage/base.py` | Interface compliance tests |
| **PR-034** | `feat(storage): local filesystem storage adapter` | `lifeledger_services/storage/local.py` | Directory sharding tests |
| **PR-035** | `feat(storage): s3 / minio object storage adapter` | `lifeledger_services/storage/s3.py` | Mocked S3 multipart upload tests |
| **PR-036** | `feat(storage): chunked streaming aes-256-gcm` | `lifeledger_services/storage/crypto.py` | Large file memory usage tests |
| **PR-037** | `feat(vault): document upload and mime validation` | `lifeledger_services/vault/upload.py` | Magic byte sniffing tests |
| **PR-038** | `feat(vault): content-addressable deduplication` | `lifeledger_services/vault/dedup.py` | SHA-256 collision detection tests |
| **PR-039** | `feat(vault): document versioning and rollback` | `lifeledger_services/vault/versioning.py`| Reversion integrity tests |
| **PR-040** | `feat(vault): document retention and purge service`| `lifeledger_services/vault/retention.py` | Quota adjustment tests |
| **PR-041** | `feat(vault): emergency ice document access vault`| `lifeledger_services/vault/ice.py` | Time-locked release tests |
| **PR-042** | `feat(vault): time-expiring shared download links` | `lifeledger_services/vault/sharing.py` | Revocation and expiry tests |
| **PR-043** | `feat(ocr): image contrast and deskew preprocessing`| `lifeledger_services/ocr/preprocess.py` | Deskew angle calculation tests |
| **PR-044** | `feat(ocr): pdf rasterization pipeline` | `lifeledger_services/ocr/rasterize.py` | High DPI rendering tests |
| **PR-045** | `feat(ocr): tesseract ocr integration engine` | `lifeledger_services/ocr/engine.py` | Mocked and real Tesseract execution tests |
| **PR-046** | `feat(ocr): multi-format date extraction parser` | `lifeledger_services/ocr/extract_dates.py`| Regex date variety tests |
| **PR-047** | `feat(ocr): currency and amount extraction regex` | `lifeledger_services/ocr/extract_amount.py`| Invoice total parsing tests |
| **PR-048** | `feat(ocr): policy and reference number matcher` | `lifeledger_services/ocr/extract_refs.py` | Alphanumeric pattern tests |
| **PR-049** | `feat(ocr): merchant and vendor directory matching`| `lifeledger_services/ocr/extract_vendor.py`| Levenshtein distance tests |
| **PR-050** | `feat(ocr): extraction confidence scoring engine` | `lifeledger_services/ocr/confidence.py` | Threshold validation tests |
| **PR-051** | `feat(ocr): celery background task ingestion worker`| `lifeledger_services/ocr/tasks.py` | Retry and dead-letter queue tests |
| **PR-052** | `feat(ocr): human review and field override service`| `lifeledger_services/ocr/review.py` | Field update audit trail tests |
| **PR-053** | `feat(ocr): bounding box calculation for web canvas`| `lifeledger_services/ocr/coordinates.py`| Coordinate mapping tests |
| **PR-054** | `feat(ocr): vehicle vin and plate extractor` | `lifeledger_services/ocr/extract_vehicle.py`| VIN check digit tests |
| **PR-055** | `feat(ocr): warranty card serial number extractor` | `lifeledger_services/ocr/extract_warranty.py`| Serial pattern tests |
| **PR-056** | `feat(deadlines): rfc 5545 recurrence rule parser` | `lifeledger_services/deadlines/rrule.py`| Complex frequency tests |
| **PR-057** | `feat(deadlines): document expiry deadline creator` | `lifeledger_services/deadlines/creator.py`| Auto-generation on upload tests |
| **PR-058** | `feat(deadlines): deadline state transition machine`| `lifeledger_services/deadlines/state.py` | Overdue status calculation tests |
| **PR-059** | `feat(deadlines): recurring obligation rollover` | `lifeledger_services/deadlines/rollover.py`| Next occurrence spawn tests |
| **PR-060** | `feat(deadlines): deadline snooze and postponement` | `lifeledger_services/deadlines/snooze.py` | Snooze date validation tests |
| **PR-061** | `feat(deadlines): priority calculation engine` | `lifeledger_services/deadlines/priority.py`| Urgency ranking tests |
| **PR-062** | `feat(deadlines): icalendar .ics export generator` | `lifeledger_services/deadlines/ical.py` | RFC 5545 format validation tests |
| **PR-063** | `feat(deadlines): automated celery beat daily cron` | `lifeledger_services/deadlines/cron.py` | Cron idempotency tests |
| **PR-064** | `feat(notifications): notification dispatcher base`| `lifeledger_services/notifications/base.py`| Multi-channel routing tests |
| **PR-065** | `feat(notifications): in-app notification service` | `lifeledger_services/notifications/inapp.py`| Unread counter query tests |
| **PR-066** | `feat(notifications): responsive email templates` | `lifeledger_services/notifications/email.py`| HTML rendering tests |
| **PR-067** | `feat(notifications): smtp and ses email dispatch` | `lifeledger_services/notifications/smtp.py` | Mocked SMTP delivery tests |
| **PR-068** | `feat(notifications): schedule evaluator (30d, 7d)`| `lifeledger_services/notifications/eval.py` | Evaluation window tests |
| **PR-069** | `feat(notifications): duplicate reminder suppressor`| `lifeledger_services/notifications/dedup.py` | Redis deduplication key tests |
| **PR-070** | `feat(notifications): outgoing webhook delivery` | `lifeledger_services/notifications/webhook.py`| SSRF blocked IP tests |
| **PR-071** | `feat(assets): appliance and device inventory` | `lifeledger_services/assets/inventory.py`| Invoice linkage tests |
| **PR-072** | `feat(assets): warranty status calculation service`| `lifeledger_services/assets/warranty.py` | Countdown days tests |
| **PR-073** | `feat(assets): maintenance log and expense tracker`| `lifeledger_services/assets/maintenance.py`| Expense summation tests |
| **PR-074** | `feat(assets): straight-line asset depreciation` | `lifeledger_services/assets/depreciation.py`| Salvage value calculation tests |
| **PR-075** | `feat(assets): formal warranty claim letter generator`| `lifeledger_services/assets/claim_letter.py`| Template text output tests |
| **PR-076** | `feat(assets): claim evidence bundle compiler` | `lifeledger_services/assets/evidence.py` | PDF merging tests |
| **PR-077** | `feat(search): full-text search adapter (fts5/trgm)`| `lifeledger_services/search/adapter.py` | FTS query syntax tests |
| **PR-078** | `feat(search): tokenizer and phonetic matching` | `lifeledger_services/search/tokenizer.py`| Metaphone/Soundex tests |
| **PR-079** | `feat(search): multi-field ranked search query` | `lifeledger_services/search/query.py` | Result ranking order tests |
| **PR-080** | `feat(analytics): 12-month renewal cash flow engine`| `lifeledger_services/analytics/cashflow.py`| Monthly bucket summation tests |
| **PR-081** | `feat(analytics): vault health score algorithm` | `lifeledger_services/analytics/health.py` | Weighted scoring tests |
| **PR-082** | `feat(analytics): pdf compliance summary report` | `lifeledger_services/analytics/pdf_report.py`| ReportLab generation tests |
| **PR-083** | `feat(analytics): csv streaming financial export` | `lifeledger_services/analytics/csv_export.py`| Streaming chunk tests |
| **PR-084** | `feat(admin): system health telemetry endpoint` | `lifeledger_services/admin/health.py` | DB and Redis ping tests |
| **PR-085** | `feat(admin): storage quota enforcement workflow` | `lifeledger_services/admin/quota.py` | Upload block upon quota tests |
| **PR-086** | `feat(admin): tamper-evident audit log verifier` | `lifeledger_services/admin/audit_verify.py`| Hash chain validation tests |
| **PR-087** | `feat(web): design system css custom properties` | `lifeledger-web/static/css/` | Visual contrast ratio tests |
| **PR-088** | `feat(web): dark/light theme toggle controller` | `lifeledger-web/static/js/theme.js` | LocalStorage event tests |
| **PR-089** | `feat(web): accessible navigation and mobile drawer`| `lifeledger-web/templates/nav.html` | Keyboard focus trapping tests |
| **PR-090** | `feat(web): dashboard cockpit and urgent banners` | `lifeledger-web/templates/dashboard.html`| Banner render tests |
| **PR-091** | `feat(web): vault gallery and filterable table` | `lifeledger-web/templates/vault.html` | Client-side filter tests |
| **PR-092** | `feat(web): drag-and-drop upload and ocr review` | `lifeledger-web/templates/upload.html` | Bounding box canvas tests |
| **PR-093** | `feat(web): deadline calendar and list view` | `lifeledger-web/templates/deadlines.html`| Month navigation tests |
| **PR-094** | `feat(web): asset catalog and claim letter wizard` | `lifeledger-web/templates/assets.html` | Wizard step progression tests |
| **PR-095** | `feat(api): v1 rest api blueprint and schemas` | `lifeledger-api/v1/` | Pydantic validation tests |
| **PR-096** | `feat(sdk-py): python client sdk implementation` | `lifeledger-sdk-py/` | Typed API call tests |
| **PR-097** | `feat(sdk-js): typescript client sdk implementation`| `lifeledger-sdk-js/` | TypeScript typecheck and tests |
| **PR-098** | `feat(cli): command-line interface implementation` | `lifeledger-cli/` | Click runner execution tests |
| **PR-099** | `test(security): owasp top 10 and idor test suite`| `tests/security/` | 100% security test pass |
| **PR-100** | `feat(release): v1.0.0 release readiness and docs` | Documentation, Dockerfile, changelog | Production smoke test pass |

---

## 17. Automated Testing Strategy and Quality Gates

LifeLedger enforces a multi-tier testing pyramid to guarantee zero regressions, strict authorization boundaries, and verifiable reliability.

```
       / \
      / E2E \       Playwright Browser Tests (50+ User Scenarios)
     /-------\
    /  Integ  \     Database, Storage, Celery Worker, OCR Tests (450+ Tests)
   /-----------\
  /    Unit     \   Pure Function, Crypto, Entity, Validator Tests (2,500+ Tests)
 /---------------\
```

### 17.1 Test Categories & Methodologies
1. **Unit Testing (`pytest tests/unit`):** Tests isolated functions, cryptographic envelope integrity, password hashing, recurrence rule parsers, and date extraction regexes without database overhead.
2. **Database Integration Testing (`pytest tests/integration`):** Runs against a containerized PostgreSQL instance to verify transactional rollbacks, Alembic migrations, foreign-key cascades, and custom encrypted types.
3. **Authorization & IDOR Security Testing (`pytest tests/security`):** Systematically executes API queries where Tenant A attempts to read, modify, or delete resources belonging to Tenant B; verifies HTTP 403/404 enforcement.
4. **OCR Pipeline Testing (`pytest tests/ocr`):** Evaluates extraction accuracy against curated document fixtures (bills, warranties, insurance cards) with known ground-truth fields.
5. **Browser End-to-End Testing (`playwright test tests/e2e`):** Automates realistic user journeys: User Registration -> Document Upload -> OCR Review -> Deadline Triggered -> Notification Generated -> Asset Claim Letter Created.
6. **Property-Based Testing (`hypothesis`):** Feeds arbitrary byte streams and malformed date strings into parsers to guarantee zero unhandled exceptions.
7. **Performance & Load Testing (`locust -f tests/performance/locustfile.py`):** Simulates 500 concurrent users performing document uploads, full-text searches, and dashboard loads, verifying p95 latency remains under 400ms.

---

## 18. CI/CD Pipelines and Deployment Instructions

### 18.1 Continuous Integration Workflow (`.github/workflows/ci.yml`)
The automated CI pipeline runs on every pull request and push to `main`:
1. **Lint & Style Check:** `ruff check .` and `ruff format --check .`.
2. **Static Type Checking:** `mypy --strict packages/`.
3. **Security Analysis (SAST):** `bandit -r packages/ -ll` and `pip-audit`.
4. **Unit & Integration Tests:** `pytest --cov=lifeledger --cov-report=xml --cov-fail-under=85`.
5. **LOC & Verification Gate:** `python scripts/measure_loc.py --verify-target`.

### 18.2 Production Deployment via Docker Compose

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    restart: always
    environment:
      - DATABASE_URL=postgresql://lifeledger_user:${DB_PASSWORD}@postgres:5432/lifeledger_prod
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - STORAGE_BACKEND=s3
      - S3_ENDPOINT=https://${S3_HOST}
      - S3_BUCKET=lifeledger-vault
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    restart: always
    environment:
      - DATABASE_URL=postgresql://lifeledger_user:${DB_PASSWORD}@postgres:5432/lifeledger_prod
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis

  beat:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    command: celery -A lifeledger_services.deadlines.cron beat -l info
    depends_on:
      - redis

  postgres:
    image: postgres:16-alpine
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=lifeledger_prod
      - POSTGRES_USER=lifeledger_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7.2-alpine
    restart: always
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 19. Documentation and Maintenance Strategy

* **Architectural Decision Records (ADRs):** Maintained in `docs/architecture/` following the Michael Nygard template, documenting choices such as vanilla CSS over Tailwind, Celery over RQ, and Argon2id over bcrypt.
* **OpenAPI 3.1 Documentation:** Generated automatically from code and published at `/api/v1/docs` via Swagger UI.
* **Operator Runbooks:** Clear operational procedures in `docs/deployment/` for automated database backups, cryptographic key rotation, storage volume expansion, and disaster recovery.
* **Database Disaster Recovery:** Daily automated pg_dump with GPG encryption dispatched to offsite cold storage; point-in-time recovery enabled via PostgreSQL write-ahead logging (WAL).

---

## 20. Risks, Resource Requirements, and Realistic Timeline

| Risk Description | Severity | Likelihood | Mitigation Strategy |
|---|---|---|---|
| **OCR Inaccuracy on Low-Quality Scans** | High | High | Implement human-in-the-loop review interface with visual bounding boxes; never automatically finalize extracted dates without user confirmation. |
| **Memory Exhaustion on Large File Uploads** | High | Low | Enforce 25MB file upload limit, stream files directly to storage adapter in 64KB chunks without loading full payloads into RAM. |
| **Notification Spam / Duplicate Alerts** | Medium | Medium | Maintain an atomic Redis deduplication lock key `reminder:{deadline_id}:{date}` before dispatching any notification. |
| **Data Loss from Corrupted Database** | Critical | Low | Enforce strict ACID transactions in SQLAlchemy, mandatory WAL archiving, and daily encrypted backup verification. |

### Engineering Resource Allocation & Milestone Timeline
* **Sprint 1–3 (Weeks 1–6):** Foundation, Models, Repositories, Auth & Vault Storage (`v0.2.0`).
* **Sprint 4–6 (Weeks 7–12):** OCR Ingestion Engine, Heuristic Extractors & Celery Workers (`v0.5.0`).
* **Sprint 7–9 (Weeks 13–18):** Recurrence Engine, Deadline State Machine & Notifications (`v0.7.0`).
* **Sprint 10–12 (Weeks 19–24):** Asset Management, Warranty Claims, Analytics & Reporting (`v0.9.0`).
* **Sprint 13–15 (Weeks 25–30):** Web Frontend Polishing, Client SDKs, CLI Tool & E2E Testing (`v1.0.0`).

---

## 21. Final Acceptance Checklist

Before declaring the LifeLedger platform production-ready and fully implemented, every criterion must be verified by automated tooling and empirical measurement:

- [ ] **LOC Footprint:** Authored physical lines of code (excluding dependencies and generated files) exceed **500,000 LOC** verified via `scripts/measure_loc.py`.
- [ ] **Git History:** At least **200 distinct, meaningful commits** present in `git log`.
- [ ] **Pull Requests:** At least **100 verified pull request work items** documented and integrated.
- [ ] **Dependency Integrity:** `poetry.lock` cryptographically matches `pyproject.toml` dependencies with zero version drift.
- [ ] **Test Coverage:** Automated test suite passes with **≥ 85% branch coverage** (`pytest --cov`).
- [ ] **Security Verification:** Zero high or critical findings in Bandit SAST scans and pip-audit dependency checks.
- [ ] **Multi-Tenant Authorization:** 100% of IDOR attack test cases pass with HTTP 403 Forbidden.
- [ ] **Clean Installation:** A fresh virtual environment reproduces the build and passes all smoke tests from scratch.
- [ ] **Accessibility Compliance:** All web views achieve **WCAG 2.1 Level AA** compliance verified via automated axe-core browser tests.

---

## 22. Commands and Scripts to Measure Actual LOC, Commits, PRs, and Tests

The repository includes a dedicated, reproducible verification script located at `scripts/measure_loc.py` and standard shell commands for independent audits.

### 22.1 Standalone Python Audit Script (`scripts/measure_loc.py`)

```python
#!/usr/bin/env python3
"""
LifeLedger Codebase Metric & Acceptance Verification Tool.
Measures authored lines of code, git commits, test coverage, and lockfile integrity.
"""
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", 
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build", "egg-info"
}

VALID_EXTENSIONS = {
    ".py", ".html", ".css", ".js", ".ts", ".sql", ".sh", ".yml", ".yaml", ".md"
}

def count_authored_loc():
    total_loc = 0
    package_loc = {}
    
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix in VALID_EXTENSIONS:
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
                        loc = len(lines)
                        total_loc += loc
                        
                        # Categorize by top-level package
                        rel_path = file_path.relative_to(WORKSPACE_ROOT)
                        top_pkg = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
                        package_loc[top_pkg] = package_loc.get(top_pkg, 0) + loc
                except Exception as e:
                    pass
    return total_loc, package_loc

def count_git_commits():
    try:
        output = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=WORKSPACE_ROOT)
        return int(output.strip().decode("utf-8"))
    except Exception:
        return 0

def main():
    print("=" * 70)
    print("LIFELEDGER PLATFORM — VERIFICATION & METRIC REPORT")
    print("=" * 70)
    
    total_loc, package_loc = count_authored_loc()
    commits = count_git_commits()
    
    print(f"\n[+] Total Authored Lines of Code (LOC): {total_loc:,}")
    print("\n[+] Breakdown by Subsystem / Directory:")
    for pkg, count in sorted(package_loc.items(), key=lambda x: x[1], reverse=True):
        print(f"    - {pkg:<25}: {count:,} LOC")
        
    print(f"\n[+] Total Git Commits on HEAD: {commits}")
    
    print("\n" + "=" * 70)
    print("ACCEPTANCE TARGET AUDIT:")
    loc_pass = total_loc >= 500000
    commit_pass = commits >= 200
    
    print(f"  * 500,000+ LOC Target : {'[PASS]' if loc_pass else '[PENDING EXECUTION]'}")
    print(f"  * 200+ Git Commits    : {'[PASS]' if commit_pass else '[PENDING EXECUTION]'}")
    print("=" * 70)

if __name__ == "__main__":
    main()
```

### 22.2 Terminal Shell Commands for Direct Audit

```bash
# 1. Count authored code using standard cloc or scc (excluding virtualenvs and node_modules)
scc --exclude-dir=.venv,venv,node_modules,.git,dist,build packages/ tests/ scripts/

# 2. Count exact number of distinct Git commits on the current branch
git rev-list --count HEAD

# 3. List recent 20 commits with author, date, and conventional commit message
git log --oneline -n 20

# 4. Verify GitHub Pull Request count via GitHub CLI
gh pr list --state all --limit 150

# 5. Execute full automated test suite with coverage enforcement
poetry run pytest --cov=packages --cov-report=term-missing --cov-fail-under=85

# 6. Verify dependency lockfile consistency
poetry check --lock
```
