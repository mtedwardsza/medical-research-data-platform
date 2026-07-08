# Data Dictionary
## Medical Research Data Platform
**Harry Perkins Institute of Medical Research — Perth, WA**

| | |
|---|---|
| **Version** | 1.0 |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy |
| **Author** | Maria Trinidad Edwards |
| **Last Updated** | July 8, 2026 |

---

## Entity Relationship Overview

```
researchers
    └── studies          (principal_researcher_id → researchers.researcher_id)
            └── participants  (study_id → studies.study_id)
                    ├── outcomes    (participant_id → participants.participant_id)
                    └── biosamples  (participant_id → participants.participant_id)
```

---

## Table: researchers

Represents research staff members at the Harry Perkins Institute.
One researcher can lead multiple studies.

| Column | Type | Nullable | Unique | Description |
|---|---|---|---|---|
| id | INTEGER | NO | YES | Internal surrogate primary key (auto-increment) |
| researcher_id | INTEGER | NO | YES | Business identifier from source system. Used as FK target |
| title | VARCHAR(20) | YES | NO | Academic title (e.g. Dr, Prof, A/Prof) |
| first_name | VARCHAR(100) | YES | NO | Researcher's given name |
| last_name | VARCHAR(100) | NO | NO | Researcher's family name |
| department | VARCHAR(100) | NO | NO | Department name (e.g. Oncology, Genomics, Cardiology) |
| email | VARCHAR(200) | YES | YES | Institutional email address |
| phone | VARCHAR(50) | YES | NO | Contact phone number |
| hire_date | DATE | YES | NO | Date the researcher joined the institute |
| is_active | BOOLEAN | YES | NO | True if currently employed. Default: True |
| orcid_id | VARCHAR(50) | YES | NO | ORCID — Open Researcher and Contributor ID (global unique identifier) |

**Source file:** `Data/raw/researchers.csv`
**Records:** 520 raw → 500 after deduplication
**Departments:** Clinical Trials (76), Epidemiology (68), Oncology (65), Biostatistics (62), Neuroscience (62), Immunology (60), Cardiology (58), Genomics (49)

---

## Table: studies

Represents clinical research studies managed at the institute.
Each study has one principal researcher and can enrol multiple participants.

| Column | Type | Nullable | Unique | Description |
|---|---|---|---|---|
| id | INTEGER | NO | YES | Internal surrogate primary key (auto-increment) |
| study_id | INTEGER | NO | YES | Business identifier from source system |
| title | VARCHAR(500) | NO | NO | Full title of the clinical study |
| phase | VARCHAR(20) | YES | NO | Clinical trial phase: Phase I, Phase II, Phase III, Phase IV |
| status | VARCHAR(50) | YES | NO | Current status: Active, Recruiting, Paused, Completed, Terminated |
| principal_researcher_id | INTEGER | NO | NO | FK → researchers.researcher_id. The lead researcher responsible for the study |
| start_date | DATE | NO | NO | Study commencement date |
| end_date | DATE | YES | NO | Planned or actual study end date. Null if ongoing |
| target_participants | INTEGER | YES | NO | Number of participants the study aims to enrol |
| ethics_approved | BOOLEAN | YES | NO | True if ethics approval has been granted. Default: False |
| budget_aud | NUMERIC(12,2) | YES | NO | Allocated budget in Australian Dollars |

**Source file:** `Data/raw/studies.csv`
**Records:** 200
**Status distribution:** Paused (47), Recruiting (46), Terminated (45), Active (32), Completed (30)
**Phase distribution:** Phase I (57), Phase IV (54), Phase II (48), Phase III (41)
**Total budget:** $184,235,423 AUD

---

## Table: participants

Represents individuals enrolled in clinical studies.
Each participant belongs to one study and can have multiple outcomes and biosamples.

| Column | Type | Nullable | Unique | Description |
|---|---|---|---|---|
| id | INTEGER | NO | YES | Internal surrogate primary key (auto-increment) |
| participant_id | INTEGER | NO | YES | Business identifier from source system |
| study_id | INTEGER | NO | NO | FK → studies.study_id. The study this participant is enrolled in |
| first_name | VARCHAR(100) | YES | NO | Participant's given name |
| last_name | VARCHAR(100) | YES | NO | Participant's family name |
| age | INTEGER | YES | NO | Age in years at time of enrolment |
| gender | VARCHAR(20) | YES | NO | Normalised gender: Male, Female, Non-binary |
| postcode | VARCHAR(10) | YES | NO | Australian postcode of participant's residence |
| primary_condition | VARCHAR(100) | YES | NO | Primary medical condition being studied (e.g. Lung Cancer, Type 2 Diabetes) |
| enrolment_date | DATE | NO | NO | Date the participant was formally enrolled in the study |
| consent_given | BOOLEAN | NO | NO | True if informed consent has been obtained. Default: True |
| withdrawn | BOOLEAN | YES | NO | True if participant has withdrawn from the study. Default: False |

**Source file:** `Data/raw/participants.csv`
**Records:** 3,040 raw → 3,000 after deduplication
**Gender split:** Female (984), Male (957), Non-binary (924)
**Withdrawn:** 250 (8.3%)
**Average age:** 52.1 years
**Top conditions:** Parkinson's Disease (303), Lung Cancer (284), Type 2 Diabetes (282), Melanoma (280)

---

## Table: outcomes

Represents individual clinical measurements recorded for a participant.
Each outcome is a single test result (e.g. a blood glucose reading on a specific date).

| Column | Type | Nullable | Unique | Description |
|---|---|---|---|---|
| id | INTEGER | NO | YES | Internal surrogate primary key (auto-increment) |
| outcome_id | INTEGER | NO | YES | Business identifier from source system |
| participant_id | INTEGER | NO | NO | FK → participants.participant_id |
| measurement_type | VARCHAR(200) | NO | NO | Type of clinical measurement (e.g. Blood Glucose (fasting), BMI, Tumour Size) |
| value | FLOAT | YES | NO | Numeric result of the measurement |
| unit | VARCHAR(50) | YES | NO | Unit of measurement (e.g. mmol/L, kg/m², mm) |
| measurement_date | DATE | NO | NO | Date the measurement was taken |
| within_normal_range | BOOLEAN | YES | NO | True if the value falls within the clinically accepted reference range |
| notes | TEXT | YES | NO | Free-text clinician notes. Null if no notes recorded |

**Source file:** `Data/raw/outcomes.csv`
**Records:** 5,060 raw → 5,000 after deduplication
**Normal range:** 3,514 (70.3%) within range · 1,486 (29.7%) abnormal
**Measurement types:** BMI (470), Blood Glucose (467), Cholesterol LDL (465), BP Diastolic (464), Cognitive Score (460), BP Systolic (458), PSA Level (458), Tumour Size (451)

---

## Table: biosamples

Represents biological specimens collected from participants and stored in the biobank.
Each biosample belongs to one participant.

| Column | Type | Nullable | Unique | Description |
|---|---|---|---|---|
| id | INTEGER | NO | YES | Internal surrogate primary key (auto-increment) |
| biosample_id | INTEGER | NO | YES | Business identifier from source system |
| participant_id | INTEGER | NO | NO | FK → participants.participant_id |
| sample_type | VARCHAR(100) | NO | NO | Type of biological specimen: Blood, Bone Marrow, Urine, Saliva, Stool, Tissue, CSF |
| collection_date | DATE | NO | NO | Date the sample was collected |
| status | VARCHAR(50) | YES | NO | Current state: Collected, Processing, Stored, Analysed, Lost, Destroyed |
| storage_location | VARCHAR(100) | YES | NO | Physical storage location (e.g. Freezer A, Freezer C) |
| volume_ml | FLOAT | YES | NO | Volume of the specimen collected, in millilitres |
| processing_cost | NUMERIC(10,2) | YES | NO | Cost to process the sample, in Australian Dollars |
| is_viable | BOOLEAN | YES | NO | True if the sample is still usable for analysis. Default: True |
| lab_technician | VARCHAR(200) | YES | NO | Full name of the technician who collected or processed the sample |

**Source file:** `Data/raw/biosamples.csv`
**Records:** 3,500
**Sample types:** Blood (534), Bone Marrow (508), Urine (507), Saliva (497), Stool (489), Tissue (487), CSF (478)
**Status:** Collected (620), Processing (594), Lost (589), Analysed (568), Stored (566), Destroyed (563)
**Viable:** 3,155 (90.1%) · Average processing cost: $422.71 AUD

---

## Data Quality Rules Applied (ETL)

| Rule | Applied To | Description |
|---|---|---|
| Date normalisation | All tables | 3 input formats → ISO `YYYY-MM-DD` |
| Boolean normalisation | is_active, ethics_approved, consent_given, withdrawn, within_normal_range, is_viable | Yes/Y/1/TRUE/True → True |
| Currency parsing | budget_aud, processing_cost | `$1,234.56` → `1234.56` |
| Gender normalisation | participants.gender | Male/MALE/M → Male |
| Whitespace trimming | All string columns | Leading/trailing spaces removed |
| Deduplication | All tables | Duplicate rows removed by primary key |
| Null drop | Critical fields | Rows with null PKs or mandatory FKs dropped |
