# Medical Research Data Migration Platform

A Business Analyst portfolio project simulating a real-world data migration for a medical research institute.

## What This Project Does

This project solves a common problem in healthcare ICT: legacy clinical data stored in messy, inconsistent CSV files needs to be migrated into a modern, centralised database — and then visualised through an analytics dashboard.

It covers the full journey:

1. **Generate** → Create realistic (but fake) clinical research data with intentional quality issues
2. **Clean** → Run an ETL pipeline to fix all data problems
3. **Store** → Load clean data into a PostgreSQL database
4. **Serve** → Expose data through a REST API
5. **Visualise** → Display insights in an analytics dashboard

## Why This Project Exists

As a Business Analyst working in a medical research ICT environment, core responsibilities include:
- Analysing data to identify trends and insights
- Improving ICT processes and workflows
- Translating business needs into technical solutions
- Documenting requirements clearly for both technical and non-technical stakeholders

This project demonstrates all of those skills in a practical, end-to-end scenario.

## The Dataset

The project uses 5 synthetic datasets representing a fictional medical research institute:

| Dataset | Records | Description |
|---------|---------|-------------|
| researchers.csv | 500 | Research staff — names, departments, credentials |
| studies.csv | 200 | Clinical studies — phases, status, dates |
| participants.csv | 3,000 | Study participants — demographics, enrolment |
| outcomes.csv | 5,000 | Measured results per participant |
| biosamples.csv | 3,500 | Biological samples — collection and lab results |

## Technology Stack

| Tool | Purpose |
|------|---------|
| Python | Data generation and ETL pipeline |
| Pandas | Data cleaning and transformation |
| PostgreSQL | Relational database |
| SQLAlchemy | Database models (ORM) |
| Flask | REST API |
| Docker | Containerised database environment |
| Jupyter Notebooks | Data profiling and analysis |

## Project Structure

```
medical-research-data-platform/
│
├── README.md               ← You are here
├── requirements.txt        ← Python packages needed
├── .gitignore              ← Files NOT uploaded to GitHub
│
├── generate_data.py        ← Step 1: Create synthetic datasets
├── process_data.py         ← Step 2: ETL cleaning pipeline
├── load_data.py            ← Step 3: Load into PostgreSQL
├── app.py                  ← Step 4: Start the Flask API
│
├── Data/
│   ├── raw/                ← Output of generate_data.py (dirty data)
│   └── processed/          ← Output of process_data.py (clean data)
│
├── models/                 ← Database table definitions
├── app/                    ← Flask application code
├── docs/                   ← Business Analyst documentation
└── Notebooks/              ← Data analysis notebooks
```

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Step 1 — Generate synthetic data
python generate_data.py

# Step 2 — Clean the data
python process_data.py

# Step 3 — Start the database (requires Docker)
docker-compose up -d

# Step 4 — Load data into the database
python load_data.py

# Step 5 — Start the API and dashboard
python app.py
```

Then open your browser at `http://localhost:5000`

---

Built by **Maria Trinidad Edwards** | Business Analyst Portfolio Project

*Domain: Medical Research | Stack: Python · PostgreSQL · Flask · Docker*
