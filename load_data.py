"""
load_data.py
============
Bulk-loads the cleaned CSV files (from Data/processed/) into PostgreSQL
using SQLAlchemy ORM models.

WHY THIS ORDER MATTERS (Foreign Key constraints):
    1. researchers   — no dependencies
    2. studies       — depends on researchers (principal_researcher_id)
    3. participants  — depends on studies    (study_id)
    4. outcomes      — depends on participants (participant_id)
    5. biosamples    — depends on participants (participant_id)

Loading in any other order would raise IntegrityError (FK violation).

USAGE:
    python load_data.py

REQUIRES:
    - .env file with DATABASE_URL set (copy from .env.example)
    - PostgreSQL running (via docker-compose up -d, or locally)
    - Data/processed/ CSVs already generated (run process_data.py first)
"""

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── ORM models ────────────────────────────────────────────────────────────────
from models.researcher  import Researcher
from models.study       import Study
from models.participant import Participant
from models.outcome     import Outcome
from models.biosample   import Biosample
from app.db             import Base


# ── Configuration ─────────────────────────────────────────────────────────────
load_dotenv()                                          # reads .env file
DATABASE_URL   = os.getenv("DATABASE_URL")
PROCESSED_DIR  = os.path.join("Data", "processed")    # Data/processed/


# ── Helper ────────────────────────────────────────────────────────────────────
def load_csv(filename: str) -> pd.DataFrame:
    """Read a CSV from the processed directory and return a DataFrame."""
    path = os.path.join(PROCESSED_DIR, filename)
    df   = pd.read_csv(path)
    print(f"  Loaded {len(df):,} rows from {path}")
    return df


def bulk_insert(session, model_class, records: list[dict], label: str) -> None:
    """
    Insert a list of dicts as ORM objects.

    Uses session.bulk_insert_mappings() which is significantly faster than
    adding objects one-by-one in a loop — suitable for thousands of rows.
    """
    if not records:
        print(f"  [WARN] No records to insert for {label}")
        return
    session.bulk_insert_mappings(model_class, records)
    print(f"  ✓ Inserted {len(records):,} {label}")


# ── Per-table loaders ─────────────────────────────────────────────────────────

def load_researchers(session) -> None:
    df = load_csv("researchers.csv")

    # Convert date strings → Python date objects (NaT → None)
    df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce").dt.date

    # Convert boolean column — CSV stores True/False as strings after process_data.py
    df["is_active"] = df["is_active"].map({"True": True, "False": False, True: True, False: False})

    records = df.to_dict(orient="records")
    bulk_insert(session, Researcher, records, "researchers")


def load_studies(session) -> None:
    df = load_csv("studies.csv")

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.date
    df["end_date"]   = pd.to_datetime(df["end_date"],   errors="coerce").dt.date
    df["ethics_approved"] = df["ethics_approved"].map(
        {"True": True, "False": False, True: True, False: False}
    )

    records = df.to_dict(orient="records")
    bulk_insert(session, Study, records, "studies")


def load_participants(session) -> None:
    df = load_csv("participants.csv")

    df["enrolment_date"] = pd.to_datetime(df["enrolment_date"], errors="coerce").dt.date
    for col in ("consent_given", "withdrawn"):
        df[col] = df[col].map({"True": True, "False": False, True: True, False: False})

    records = df.to_dict(orient="records")
    bulk_insert(session, Participant, records, "participants")


def load_outcomes(session) -> None:
    df = load_csv("outcomes.csv")

    df["measurement_date"] = pd.to_datetime(df["measurement_date"], errors="coerce").dt.date
    df["within_normal_range"] = df["within_normal_range"].map(
        {"True": True, "False": False, True: True, False: False}
    )

    # notes column may have NaN — replace with None so SQLAlchemy stores NULL
    df["notes"] = df["notes"].where(df["notes"].notna(), None)

    records = df.to_dict(orient="records")
    bulk_insert(session, Outcome, records, "outcomes")


def load_biosamples(session) -> None:
    df = load_csv("biosamples.csv")

    df["collection_date"] = pd.to_datetime(df["collection_date"], errors="coerce").dt.date
    df["is_viable"] = df["is_viable"].map(
        {"True": True, "False": False, True: True, False: False}
    )

    records = df.to_dict(orient="records")
    bulk_insert(session, Biosample, records, "biosamples")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if not DATABASE_URL:
        raise EnvironmentError(
            "DATABASE_URL not set. Copy .env.example → .env and fill in your values."
        )

    print(f"\nConnecting to database…")
    engine  = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)

    # Create all tables defined in ORM models (safe no-op if they already exist)
    print("Creating tables (if not exist)…")
    Base.metadata.create_all(engine)

    print("\nLoading data in FK order:\n")
    with Session() as session:
        try:
            load_researchers(session)
            load_studies(session)
            load_participants(session)
            load_outcomes(session)
            load_biosamples(session)

            session.commit()
            print("\n✅ All data loaded successfully.")

        except Exception as exc:
            session.rollback()
            print(f"\n❌ Load failed — rolled back. Error: {exc}")
            raise


if __name__ == "__main__":
    main()
