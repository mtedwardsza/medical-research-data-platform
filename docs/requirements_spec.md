# Requirements Specification
## Medical Research Data Platform
**Harry Perkins Institute of Medical Research — Perth, WA**

| | |
|---|---|
| **Version** | 1.0 |
| **Status** | In Progress |
| **Sprint** | Sprint 1 (Jun 20 – Jul 10, 2026) |
| **Author** | Maria Trinidad Edwards |
| **Role** | Business Analyst |

---

## 1. Project Overview

### 1.1 Background

The Harry Perkins Institute of Medical Research manages clinical research data across multiple departments, studies, participants, and biosamples. Legacy data was stored in flat CSV files with inconsistent formats, no referential integrity, and no centralised access layer. This created significant manual effort for researchers and analysts trying to extract insights.

### 1.2 Objective

Design and deliver an end-to-end data platform that:
- Migrates raw legacy CSV data into a structured relational database
- Exposes data through a secure REST API
- Provides an analytics dashboard for research oversight
- Enforces role-based access control

### 1.3 Scope

**In scope:**
- ETL pipeline for 5 CSV datasets (researchers, studies, participants, outcomes, biosamples)
- PostgreSQL relational schema with FK constraints
- Flask REST API with 9 endpoints
- Interactive HTML analytics dashboard
- Session-based authentication with 2 roles (admin, viewer)
- Technical documentation (requirements spec, data dictionary)
- Unit and integration tests

**Out of scope:**
- Real-time data ingestion
- Mobile application
- External integrations (ORCID API, HREC systems)
- Multi-tenant support

---

## 2. Stakeholders

| Stakeholder | Role | Interest |
|---|---|---|
| Research Director | Primary sponsor | Oversight of study portfolio and budget |
| Lab Researchers | End users | Access to their study and participant data |
| Data Analysts | End users | Dashboard and API for reporting |
| IT / DevOps | Technical | Infrastructure, deployment, security |
| Ethics Committee | Compliance | Participant data privacy and consent tracking |

---

## 3. Functional Requirements

### US-01 — Raw Data Ingestion
| ID | Requirement |
|---|---|
| FR-01 | The system shall accept 5 CSV files as input (researchers, studies, participants, outcomes, biosamples) |
| FR-02 | Raw files shall be stored in `Data/raw/` and version-controlled |
| FR-03 | Raw files shall not be modified — all transformations occur in a separate pipeline |

### US-02 — ETL Data Cleaning
| ID | Requirement |
|---|---|
| FR-04 | The system shall parse dates in 3 formats: `YYYY-MM-DD`, `DD/MM/YYYY`, `Mon-DD-YYYY` |
| FR-05 | Boolean fields shall be normalised from multiple representations (Yes/Y/1/TRUE/True → True) |
| FR-06 | Currency strings (e.g. `$793.00`) shall be converted to numeric float values |
| FR-07 | Gender values shall be normalised to: Male, Female, Non-binary |
| FR-08 | Duplicate rows shall be removed based on primary key |
| FR-09 | Rows with null values in critical fields shall be dropped |
| FR-10 | Cleaned data shall be written to `Data/processed/` |

### US-03 — Database Setup
| ID | Requirement |
|---|---|
| FR-11 | The system shall use PostgreSQL 15 as the relational database engine |
| FR-12 | All 5 entities shall be represented as ORM models using SQLAlchemy |
| FR-13 | Foreign key constraints shall be enforced between all related tables |
| FR-14 | The database shall be containerised via Docker Compose |
| FR-15 | The bulk loader shall insert records in FK-safe order |

### US-04 — REST API
| ID | Requirement |
|---|---|
| FR-16 | The system shall expose GET endpoints for all 5 entities |
| FR-17 | All list endpoints shall support optional query filters |
| FR-18 | Detail endpoints shall return related entity data (e.g. researcher's studies) |
| FR-19 | A `/api/summary` endpoint shall return platform-wide aggregate statistics |
| FR-20 | A `/api/health` endpoint shall verify database connectivity |

### US-05 — Analytics Dashboard
| ID | Requirement |
|---|---|
| FR-21 | The dashboard shall display KPI cards for all 5 entities |
| FR-22 | The dashboard shall include a minimum of 10 chart visualisations |
| FR-23 | All charts shall display percentage labels |
| FR-24 | The dashboard shall support light and dark mode toggle |
| FR-25 | The dashboard shall use the Harry Perkins Institute brand colours |

### US-06 — Authentication
| ID | Requirement |
|---|---|
| FR-26 | The system shall implement session-based authentication |
| FR-27 | Two roles shall be supported: `admin` (full access) and `viewer` (read-only) |
| FR-28 | Unauthenticated API requests shall return HTTP 401 |
| FR-29 | Unauthenticated browser requests shall redirect to `/auth/login` |
| FR-30 | Credentials shall be stored in environment variables, not in source code |

### US-07 — Documentation
| ID | Requirement |
|---|---|
| FR-31 | A requirements specification document shall describe all functional and non-functional requirements |
| FR-32 | A data dictionary shall document all tables, columns, types and business definitions |

### US-08 — Testing & QA
| ID | Requirement |
|---|---|
| FR-33 | Unit tests shall cover all ETL transformation functions |
| FR-34 | Integration tests shall verify API endpoint responses |
| FR-35 | Test coverage shall target a minimum of 80% |

---

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | API list endpoints shall respond within 500ms for up to 10,000 records |
| NFR-02 | Security | No credentials or secrets shall be committed to version control |
| NFR-03 | Security | All passwords shall be stored as environment variables |
| NFR-04 | Maintainability | All modules shall include docstrings explaining purpose and design decisions |
| NFR-05 | Portability | The full stack shall run locally via `docker-compose up` |
| NFR-06 | Usability | The dashboard shall be accessible via a standard web browser without installation |
| NFR-07 | Data Integrity | FK constraints shall prevent orphaned records in the database |
| NFR-08 | Traceability | Raw source data shall be preserved unmodified alongside cleaned data |

---

## 5. Assumptions & Constraints

**Assumptions:**
- Source data is provided as CSV files from the legacy system
- Participant consent is pre-validated before data is loaded into the platform
- The institute runs macOS or Linux for local development

**Constraints:**
- Sprint 1 delivery: 10 July 2026
- No budget allocated for cloud hosting — local Docker deployment only
- Authentication is session-based (no OAuth / SSO in scope for Sprint 1)

---

## 6. Delivery Milestones

| Milestone | Target Date | Status |
|---|---|---|
| US-01 Raw Data Ingestion | Jun 22, 2026 | ✅ Done |
| US-02 ETL Cleaning | Jun 25, 2026 | ✅ Done |
| US-03 Database Setup | Jul 1, 2026 | ✅ Done |
| US-04 REST API | Jul 3, 2026 | ✅ Done |
| US-05 Dashboard | Jul 7, 2026 | ✅ Done |
| US-06 Authentication | Jul 8, 2026 | ✅ Done |
| US-07 Documentation | Jul 8, 2026 | ✅ Done |
| US-08 Testing & QA | Jul 10, 2026 | 🔄 In Progress |
