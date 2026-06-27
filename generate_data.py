"""
generate_data.py
================
Synthetic data generator for the Medical Research Data Migration Platform.

PURPOSE:
    Creates 5 CSV files that simulate real-world legacy data exports from a
    medical research institute. The data intentionally contains quality issues
    (mixed date formats, missing values, duplicates, etc.) to demonstrate a
    realistic ETL scenario.

    Think of this as: "what would the data look like if 10 different staff
    members entered it over 5 years with no data standards in place?"

HOW TO RUN:
    python generate_data.py

OUTPUT:
    Data/raw/researchers.csv   — 500 records
    Data/raw/studies.csv       — 200 records
    Data/raw/participants.csv  — 3,000 records
    Data/raw/outcomes.csv      — 5,000 records
    Data/raw/biosamples.csv    — 3,500 records

Author: Maria Trinidad Edwards
"""

import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
import os

# ── Reproducibility ───────────────────────────────────────────────────────────
# A "seed" makes random data reproducible — every time you run this script,
# you get exactly the same data. This is important for demos and testing.
# Without a seed, the data would be different every run.
random.seed(42)
np.random.seed(42)
fake = Faker(locale="en_AU")   # Australian locale → realistic Perth names/addresses
Faker.seed(42)

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUT_DIR = "Data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)   # Create folder if it doesn't exist

print("🔬 Medical Research Data Generator")
print("=" * 50)


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# These small functions are used repeatedly when building the datasets.
# ─────────────────────────────────────────────────────────────────────────────

def random_date(start_year=2019, end_year=2024):
    """
    Generate a random date between two years.
    Returns a Python datetime object.
    """
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def messy_date(date_obj):
    """
    Return a date in one of THREE inconsistent formats.

    WHY: This simulates the real-world problem of different staff entering
    dates in different ways over the years. The ETL pipeline (process_data.py)
    must detect and fix all three formats.

    Formats:
        2023-05-20      ← ISO format (international standard)
        20/05/2023      ← Australian common format
        May-20-2023     ← US-style abbreviated month
    """
    formats = [
        "%Y-%m-%d",    # ISO — most systems use this
        "%d/%m/%Y",    # Australian — very common in WA
        "%b-%d-%Y",    # US abbreviated — sometimes imported from US systems
    ]
    return date_obj.strftime(random.choice(formats))


def messy_bool(value):
    """
    Return a boolean value in one of many inconsistent string formats.

    WHY: Different systems export booleans differently.
    A "Yes" in one system might be "1" or "TRUE" in another.
    The ETL must standardise all of these to Python True/False.
    """
    if value:
        return random.choice(["Yes", "Y", "1", "True", "TRUE", True])
    else:
        return random.choice(["No", "N", "0", "False", "FALSE", False])


def messy_currency(amount):
    """
    Return a numeric amount as a messy currency string.

    WHY: Legacy systems often export numbers as formatted currency strings.
    "$2,450.00" looks nice in a report but breaks any numeric calculation.
    The ETL must strip "$" and "," and convert to float.
    """
    return f"${amount:,.2f}"


def messy_gender():
    """
    Return gender in one of many inconsistent formats.

    WHY: Over years, staff entered gender differently.
    The ETL normalises all variants to: "Male", "Female", "Non-binary"
    """
    options = {
        "Male":       ["Male", "MALE", "male", "M", "m"],
        "Female":     ["Female", "FEMALE", "female", "F", "f"],
        "Non-binary": ["Non-binary", "NB", "non-binary", "Other"]
    }
    gender = random.choice(list(options.keys()))
    return random.choice(options[gender])


def maybe_null(value, probability=0.05):
    """
    Return None (missing value) with a given probability.

    WHY: Real-world data always has missing values — staff forget to fill
    fields, systems fail to export them, or they simply weren't collected.
    probability=0.05 means ~5% of values will be missing.
    """
    return None if random.random() < probability else value


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 1 — RESEARCHERS
# Research staff at the institute. These are the "parent" records —
# every Study must have a principal researcher.
# ─────────────────────────────────────────────────────────────────────────────

def generate_researchers(n=500):
    print(f"\n📋 Generating {n} researcher records...")

    departments = [
        "Oncology", "Cardiology", "Neuroscience", "Immunology",
        "Genomics", "Epidemiology", "Biostatistics", "Clinical Trials"
    ]
    titles = ["Dr.", "Prof.", "A/Prof.", "Mr.", "Ms.", "Mrs."]

    records = []
    for i in range(1, n + 1):
        records.append({
            "researcher_id":  i,
            "title":          random.choice(titles),
            "first_name":     maybe_null(fake.first_name(), 0.02),
            "last_name":      fake.last_name(),
            "department":     random.choice(departments),
            "email":          maybe_null(fake.email().lower(), 0.03),
            "phone":          maybe_null(fake.phone_number(), 0.08),
            "hire_date":      messy_date(random_date(2010, 2023)),
            "is_active":      messy_bool(random.random() > 0.15),
            "orcid_id":       maybe_null(f"0000-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}", 0.3),
        })

    df = pd.DataFrame(records)

    # ── Introduce 20 duplicate researchers ───────────────────────────────────
    # WHY: Duplicates happen when data is imported from multiple systems.
    # The ETL must detect and remove them.
    duplicates = df.sample(20).copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    df.to_csv(f"{OUTPUT_DIR}/researchers.csv", index=False)
    print(f"   ✓ {len(df)} rows written (including 20 duplicates)")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 2 — STUDIES
# Clinical trials. Each study has one principal researcher.
# Phases I-IV reflect real clinical trial progression.
# ─────────────────────────────────────────────────────────────────────────────

def generate_studies(researchers_df, n=200):
    print(f"\n🔬 Generating {n} clinical study records...")

    researcher_ids = researchers_df["researcher_id"].tolist()
    phases = ["Phase I", "Phase II", "Phase III", "Phase IV"]
    statuses = ["Active", "Completed", "Paused", "Recruiting", "Terminated"]

    study_areas = [
        "Breast Cancer Immunotherapy", "Cardiovascular Risk Reduction",
        "Alzheimer's Early Detection", "Type 2 Diabetes Management",
        "Lung Cancer Biomarkers", "Parkinson's Disease Treatment",
        "COVID-19 Long-term Effects", "Melanoma Targeted Therapy",
        "Childhood Obesity Intervention", "Mental Health Digital Tools"
    ]

    records = []
    for i in range(1, n + 1):
        start = random_date(2019, 2023)
        end = start + timedelta(days=random.randint(180, 1460))  # 6 months to 4 years

        records.append({
            "study_id":             i,
            "title":                f"{random.choice(study_areas)} — Study {i:03d}",
            "phase":                random.choice(phases),
            "status":               random.choice(statuses),
            "principal_researcher": random.choice(researcher_ids),
            "start_date":           messy_date(start),
            "end_date":             maybe_null(messy_date(end), 0.2),
            "target_participants":  random.randint(20, 500),
            "ethics_approved":      messy_bool(random.random() > 0.05),
            "budget_aud":           maybe_null(messy_currency(random.randint(50000, 2000000)), 0.1),
        })

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/studies.csv", index=False)
    print(f"   ✓ {len(df)} rows written")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 3 — PARTICIPANTS
# People enrolled in studies. Each participant belongs to one study.
# Note the messy gender field — this is one of the key ETL challenges.
# ─────────────────────────────────────────────────────────────────────────────

def generate_participants(studies_df, n=3000):
    print(f"\n👥 Generating {n} participant records...")

    study_ids = studies_df["study_id"].tolist()
    conditions = [
        "Hypertension", "Type 2 Diabetes", "Breast Cancer", "Lung Cancer",
        "Alzheimer's Disease", "Parkinson's Disease", "Melanoma",
        "Cardiovascular Disease", "Obesity", "Depression", "Healthy Control"
    ]

    records = []
    for i in range(1, n + 1):
        enrol_date = random_date(2019, 2024)
        records.append({
            "participant_id":   i,
            "study_id":         random.choice(study_ids),
            "first_name":       maybe_null(fake.first_name(), 0.03),
            "last_name":        maybe_null(fake.last_name(), 0.02),
            "age":              maybe_null(random.randint(18, 85), 0.05),
            "gender":           maybe_null(messy_gender(), 0.04),
            "postcode":         maybe_null(fake.postcode(), 0.06),
            "primary_condition": random.choice(conditions),
            "enrolment_date":   messy_date(enrol_date),
            "consent_given":    messy_bool(random.random() > 0.02),
            "withdrawn":        messy_bool(random.random() < 0.08),
        })

    df = pd.DataFrame(records)

    # ── Introduce 40 duplicate participants ───────────────────────────────────
    duplicates = df.sample(40).copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    df.to_csv(f"{OUTPUT_DIR}/participants.csv", index=False)
    print(f"   ✓ {len(df)} rows written (including 40 duplicates)")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 4 — OUTCOMES
# Measured results for each participant. Multiple outcomes per participant.
# The "value" field is stored as a messy string (e.g. "$2.45") — must be
# cleaned to float by the ETL.
# ─────────────────────────────────────────────────────────────────────────────

def generate_outcomes(participants_df, n=5000):
    print(f"\n📊 Generating {n} outcome records...")

    participant_ids = participants_df["participant_id"].tolist()
    measure_types = [
        "Blood Pressure (Systolic)", "Blood Pressure (Diastolic)",
        "Blood Glucose (fasting)", "Tumour Size (mm)",
        "Cognitive Score", "Quality of Life Score",
        "Haemoglobin A1c", "Body Mass Index", "Cholesterol (LDL)",
        "PSA Level", "CD4 Cell Count"
    ]
    units = {
        "Blood Pressure (Systolic)": "mmHg",
        "Blood Pressure (Diastolic)": "mmHg",
        "Blood Glucose (fasting)": "mmol/L",
        "Tumour Size (mm)": "mm",
        "Cognitive Score": "points",
        "Quality of Life Score": "points",
        "Haemoglobin A1c": "%",
        "Body Mass Index": "kg/m²",
        "Cholesterol (LDL)": "mmol/L",
        "PSA Level": "ng/mL",
        "CD4 Cell Count": "cells/µL"
    }

    records = []
    for i in range(1, n + 1):
        measure = random.choice(measure_types)
        records.append({
            "outcome_id":       i,
            "participant_id":   random.choice(participant_ids),
            "measurement_type": measure,
            "value":            maybe_null(round(random.uniform(0.5, 300), 2), 0.06),
            "unit":             units[measure],
            "measurement_date": messy_date(random_date(2019, 2024)),
            "within_normal_range": messy_bool(random.random() > 0.3),
            "notes":            maybe_null(fake.sentence(nb_words=8), 0.6),
        })

    df = pd.DataFrame(records)

    # ── Introduce 60 duplicate outcomes ───────────────────────────────────────
    duplicates = df.sample(60).copy()
    df = pd.concat([df, duplicates], ignore_index=True)

    df.to_csv(f"{OUTPUT_DIR}/outcomes.csv", index=False)
    print(f"   ✓ {len(df)} rows written (including 60 duplicates)")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# DATASET 5 — BIOSAMPLES
# Biological samples collected from participants.
# "processing_cost" is stored as messy currency string.
# ─────────────────────────────────────────────────────────────────────────────

def generate_biosamples(participants_df, n=3500):
    print(f"\n🧪 Generating {n} biosample records...")

    participant_ids = participants_df["participant_id"].tolist()
    sample_types = ["Blood", "Tissue", "Saliva", "Urine", "CSF", "Bone Marrow", "Stool"]
    statuses = ["Collected", "Processing", "Analysed", "Stored", "Destroyed", "Lost"]
    storage_locations = ["Freezer A", "Freezer B", "Freezer C", "Lab Storage 1", "Lab Storage 2"]

    records = []
    for i in range(1, n + 1):
        collection_date = random_date(2019, 2024)
        records.append({
            "biosample_id":       i,
            "participant_id":     random.choice(participant_ids),
            "sample_type":        random.choice(sample_types),
            "collection_date":    messy_date(collection_date),
            "status":             random.choice(statuses),
            "storage_location":   maybe_null(random.choice(storage_locations), 0.1),
            "volume_ml":          maybe_null(round(random.uniform(0.5, 50.0), 2), 0.07),
            "processing_cost":    maybe_null(messy_currency(random.randint(50, 800)), 0.12),
            "is_viable":          messy_bool(random.random() > 0.1),
            "lab_technician":     maybe_null(fake.name(), 0.08),
        })

    df = pd.DataFrame(records)
    df.to_csv(f"{OUTPUT_DIR}/biosamples.csv", index=False)
    print(f"   ✓ {len(df)} rows written")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — Run all generators in order
# Order matters: researchers → studies → participants → outcomes → biosamples
# because each dataset references IDs from the previous one (foreign keys).
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    researchers = generate_researchers(500)
    studies     = generate_studies(researchers, 200)
    participants = generate_participants(studies, 3000)
    outcomes    = generate_outcomes(participants, 5000)
    biosamples  = generate_biosamples(participants, 3500)

    print("\n" + "=" * 50)
    print("✅ Data generation complete!")
    print(f"   📁 Files saved to: {OUTPUT_DIR}/")
    print(f"   📊 Total records generated:")
    print(f"      Researchers : {len(researchers):,}")
    print(f"      Studies     : {len(studies):,}")
    print(f"      Participants: {len(participants):,}")
    print(f"      Outcomes    : {len(outcomes):,}")
    print(f"      Biosamples  : {len(biosamples):,}")
    print(f"      TOTAL       : {len(researchers)+len(studies)+len(participants)+len(outcomes)+len(biosamples):,}")
    print("\n⚠️  Remember: this data contains intentional quality issues.")
    print("   Run process_data.py to clean it before loading to the database.")
