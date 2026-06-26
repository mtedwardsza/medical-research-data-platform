# 🔬 Medical Research Data Migration Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3-green?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?logo=pandas)](https://pandas.pydata.org)

> A Business Analyst portfolio project demonstrating end-to-end ownership of a clinical data migration — from raw legacy CSVs to a production-ready analytics dashboard.

---

## 📋 Overview

This project simulates a real-world challenge in healthcare ICT: **migrating legacy clinical research data** from inconsistent, messy CSV exports into a centralised, queryable PostgreSQL database — then surfacing insights through an interactive analytics dashboard.

It was built to demonstrate Business Analyst technical skills in ICT environment, covering: data analysis, ETL pipeline design, database modelling, API development, and stakeholder-facing documentation.

---

## 🏗️ Architecture — 8 Phases

**Phase 1 — Synthetic Data Generation** (`generate_data.py`)
Creates 5 interconnected CSV files with ~12,200 records simulating a medical research institute. Data contains intentional quality issues to replicate real-world legacy exports.

**Phase 2 — ETL Cleaning Pipeline** (`process_data.py`)
Extracts, transforms, and loads clean data into processed CSVs. Fixes date formats, currency strings, boolean chaos, duplicates, missing values, and invalid ranges. Logs before/after row counts.

**Phase 3 — Relational Database Design** (`models/`)
Five SQLAlchemy ORM models with proper foreign key relationships: Researcher → Study → Participant → Outcome → Biosample. Designed to reflect how a real research institute structures its data.

**Phase 4 — Database Loading** (`load_data.py`)
Bulk-inserts cleaned data into PostgreSQL respecting foreign key order. Handles constraint errors and logs insertion results per table.

**Phase 5 — Containerisation** (`docker-compose.yml`)
Docker Compose runs PostgreSQL in an isolated container — no local database install required. Consistent across all environments.

**Phase 6 — REST API** (`app/routes.py`)
8 endpoints expose the data programmatically: studies, participants, outcomes, biosamples, researchers, and a summary statistics endpoint for the dashboard.

**Phase 7 — Authentication** (`app/auth.py`)
Session-based login with two roles: Admin (full access) and Viewer (read-only dashboard).

**Phase 8 — Analytics Dashboard** (`dashboard.html`)
Interactive client-side dashboard with KPI cards, charts, searchable tables, and CSV export.

---

## 📊 Dataset — Clinical Research Domain

| File | Records | Description |
|------|---------|-------------|
| `researchers.csv` | 500 | Research staff — departments, credentials, hire dates |
| `studies.csv` | 200 | Clinical trials — Phase I–IV, status, principal researcher |
| `participants.csv` | 3,000 | Study participants — demographics, enrolment dates |
| `outcomes.csv` | 5,000 | Measured results per participant per study |
| `biosamples.csv` | 3,500 | Biological samples — collection, lab results, status |

### Data Quality Issues Introduced (simulating real-world legacy data)

| Issue | Example |
|-------|---------|
| Mixed date formats | `"2023-05-01"` / `"01/05/2023"` / `"May-01-2023"` |
| Numeric values as strings | `"$2,450.00"` instead of `2450.0` |
| Inconsistent casing | `"FEMALE"` / `"female"` / `"F"` → normalised to `"Female"` |
| Missing values | Random nulls in critical fields |
| Duplicate records | 40 duplicate participants, 60 duplicate outcomes |
| Boolean chaos | `"Yes"/"No"/"Y"/"N"/"1"/"0"` — all meaning the same thing |

---

## 🛠️ Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Data Generation | Python, Faker, NumPy | Creates realistic Australian-locale synthetic data |
| ETL Pipeline | Python, Pandas | Industry-standard for data cleaning and transformation |
| Database | PostgreSQL 15 | Robust relational database used widely in healthcare |
| ORM | SQLAlchemy | Defines database tables as Python classes |
| API | Flask | Lightweight REST framework for Python |
| Containerisation | Docker, Docker Compose | Reproducible environment, no manual DB setup |
| Analysis | Jupyter Notebooks | Data profiling and post-ETL verification |
| Frontend | HTML, CSS, JavaScript | No framework needed for a focused dashboard |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Docker Desktop
- Git

### Run the Project

```bash
# 1. Clone the repository
git clone https://github.com/mtedwardsza/medical-research-data-platform.git
cd medical-research-data-platform

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Copy environment variables
cp .env.example .env

# 4. Start PostgreSQL with Docker
docker-compose up -d

# 5. Generate synthetic data
python generate_data.py

# 6. Run ETL pipeline
python process_data.py

# 7. Load cleaned data into the database
python load_data.py

# 8. Start the Flask application
python app.py
```

Open your browser at `http://localhost:5000`

**Login credentials:**

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin2026` |
| Viewer | `viewer` | `viewer123` |

---

## 📁 Project Structure

```
medical-research-data-platform/
│
├── README.md               ← You are here
├── requirements.txt        ← Python packages needed
├── .gitignore              ← Files NOT tracked by Git
├── .env.example            ← Environment variable template
├── docker-compose.yml      ← PostgreSQL container setup
├── Dockerfile              ← App container definition
│
├── generate_data.py        ← Phase 1: Synthetic data generator
├── process_data.py         ← Phase 2: ETL cleaning pipeline
├── load_data.py            ← Phase 4: Database loader
├── app.py                  ← Flask entry point
│
├── Data/
│   ├── raw/                ← Dirty CSVs (output of generate_data.py)
│   └── processed/          ← Clean CSVs (output of process_data.py)
│
├── models/                 ← SQLAlchemy ORM table definitions
│   ├── researcher.py
│   ├── study.py
│   ├── participant.py
│   ├── outcome.py
│   └── biosample.py
│
├── app/                    ← Flask application
│   ├── routes.py           ← API endpoints
│   ├── auth.py             ← Login and role management
│   └── db.py               ← Database connection
│
├── docs/                   ← Business Analyst documentation
│   ├── requirements_spec.md     ← Functional requirements & user stories
│   └── data_dictionary.md       ← Field definitions & transformation rules
│
└── Notebooks/              ← Jupyter analysis notebooks
    ├── 01_data_profiling.ipynb
    └── 02_post_etl_verification.ipynb
```

---

## 📈 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/studies` | List all clinical studies |
| GET | `/api/studies/<id>` | Get a single study with participants |
| GET | `/api/participants` | List participants (filterable by study) |
| GET | `/api/outcomes` | Query outcomes by study or participant |
| GET | `/api/biosamples` | List biosamples with status filter |
| GET | `/api/researchers` | List research staff |
| GET | `/api/summary` | Dashboard KPI statistics |
| POST | `/api/login` | Authenticate and create session |

---

## 📚 Key Deliverables

- ✅ 5 cleaned datasets ready for analysis (~12,200 records)
- ✅ ETL pipeline with full logging and row-count validation
- ✅ Normalised PostgreSQL schema with foreign key relationships
- ✅ REST API with 8 endpoints and role-based authentication
- ✅ Interactive analytics dashboard with CSV export
- ✅ Containerised environment (Docker Compose)
- ✅ BA documentation: requirements spec + data dictionary

---

## 👩‍💼 About

Built by **Maria Trinidad Edwards** as a Business Analyst portfolio project — demonstrating data analysis, ETL pipeline design, requirements documentation, and ICT process improvement skills in a medical research context.

📧 mtedwardsza@gmail.com

---

*Domain: Medical Research · Stack: Python · PostgreSQL · Flask · Docker*
