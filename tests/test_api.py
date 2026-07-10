"""
tests/test_api.py
=================
Integration tests for the Flask REST API (app/routes.py + app/auth.py).

WHAT IS AN INTEGRATION TEST?
    Unlike unit tests (which test one function in isolation), integration tests
    verify that multiple components work together correctly. Here we test the
    full request/response cycle: HTTP request → Flask route → response.

HOW FLASK TESTING WORKS:
    Flask provides a test client that simulates HTTP requests without needing
    a real server running. We use app.test_client() to send GET/POST requests
    and assert on the response status code and JSON body.

    The test database uses SQLite in-memory (`:memory:`) so tests run fast
    and don't affect the real PostgreSQL database.

HOW TO RUN:
    pip install pytest --break-system-packages
    pytest tests/test_api.py -v

COVERAGE:
    - Health check          : 1 test
    - Auth (login/logout)   : 4 tests
    - Researchers endpoints : 3 tests
    - Studies endpoints     : 3 tests
    - Participants endpoint : 2 tests
    - Outcomes endpoint     : 2 tests
    - Biosamples endpoint   : 2 tests
    - Summary endpoint      : 1 test
    Total                   : 18 integration tests
"""

import sys
import os
import pytest

# ── Project root on path ──────────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Use SQLite in-memory for tests — no PostgreSQL needed
os.environ["DATABASE_URL"]    = "sqlite:///:memory:"
os.environ["SECRET_KEY"]      = "test-secret-key"
os.environ["ADMIN_USERNAME"]  = "admin"
os.environ["ADMIN_PASSWORD"]  = "testpass"
os.environ["VIEWER_USERNAME"] = "viewer"
os.environ["VIEWER_PASSWORD"] = "viewerpass"

from app import create_app
from app.db import Base, engine
from models.researcher  import Researcher
from models.study       import Study
from models.participant import Participant
from models.outcome     import Outcome
from models.biosample   import Biosample
from sqlalchemy.orm import sessionmaker


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    """Create a Flask test app with SQLite in-memory database."""
    flask_app = create_app()
    flask_app.config["TESTING"] = True

    # Create all tables in the test database
    Base.metadata.create_all(bind=engine)

    # Seed minimal test data
    Session = sessionmaker(bind=engine)
    db = Session()

    researcher = Researcher(
        researcher_id=1,
        first_name="Jane",
        last_name="Smith",
        department="Oncology",
        email="j.smith@perkins.org.au",
        is_active=True
    )
    study = Study(
        study_id=1,
        title="Melanoma Immunotherapy Trial",
        phase="Phase II",
        status="Active",
        principal_researcher_id=1,
        start_date="2024-01-15",
        ethics_approved=True,
        budget_aud=850000.00
    )
    participant = Participant(
        participant_id=1,
        study_id=1,
        first_name="John",
        last_name="Doe",
        age=55,
        gender="Male",
        primary_condition="Melanoma",
        enrolment_date="2024-02-01",
        consent_given=True,
        withdrawn=False
    )
    outcome = Outcome(
        outcome_id=1,
        participant_id=1,
        measurement_type="Tumour Size (mm)",
        value=12.5,
        unit="mm",
        measurement_date="2024-03-01",
        within_normal_range=True
    )
    biosample = Biosample(
        biosample_id=1,
        participant_id=1,
        sample_type="Blood",
        collection_date="2024-02-15",
        status="Stored",
        volume_ml=10.0,
        processing_cost=350.00,
        is_viable=True,
        lab_technician="Sarah Jones"
    )

    db.add_all([researcher, study, participant, outcome, biosample])
    db.commit()
    db.close()

    yield flask_app

    # Teardown — drop all tables after tests complete
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(scope="module")
def auth_client(client):
    """Test client pre-logged-in as admin."""
    client.post("/auth/login", data={
        "username": "admin",
        "password": "testpass"
    })
    return client


# ═══════════════════════════════════════════════════════════════════════════════
# Health check
# ═══════════════════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_returns_ok(self, client):
        """GET /api/health should return status ok and database connected."""
        res = client.get("/api/health")
        assert res.status_code == 200
        data = res.get_json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════

class TestAuth:
    def test_login_success(self, client):
        """Valid credentials should return 200 and set a session."""
        res = client.post("/auth/login",
                          json={"username": "admin", "password": "testpass"})
        assert res.status_code == 200
        data = res.get_json()
        assert data["role"] == "admin"

    def test_login_wrong_password(self, client):
        """Wrong password should return 401 Unauthorized."""
        res = client.post("/auth/login",
                          json={"username": "admin", "password": "wrongpass"})
        assert res.status_code == 401

    def test_login_unknown_user(self, client):
        """Unknown username should return 401 Unauthorized."""
        res = client.post("/auth/login",
                          json={"username": "hacker", "password": "abc"})
        assert res.status_code == 401

    def test_logout_clears_session(self, client):
        """After logout, /auth/me should return 401."""
        # Login first
        client.post("/auth/login",
                    json={"username": "admin", "password": "testpass"})
        # Logout
        client.get("/auth/logout")
        # Now /auth/me should be protected
        res = client.get("/auth/me")
        assert res.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# Researchers
# ═══════════════════════════════════════════════════════════════════════════════

class TestResearchers:
    def test_list_researchers_returns_200(self, auth_client):
        """GET /api/researchers should return 200 and a list."""
        res = auth_client.get("/api/researchers")
        assert res.status_code == 200
        data = res.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_researchers_has_expected_fields(self, auth_client):
        """Each researcher object should have the required fields."""
        res = auth_client.get("/api/researchers")
        researcher = res.get_json()[0]
        assert "researcher_id" in researcher
        assert "last_name"     in researcher
        assert "department"    in researcher

    def test_get_researcher_by_id(self, auth_client):
        """GET /api/researchers/1 should return the correct researcher."""
        res = auth_client.get("/api/researchers/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["researcher_id"] == 1
        assert data["last_name"] == "Smith"

    def test_get_nonexistent_researcher_returns_404(self, auth_client):
        """Requesting a researcher that doesn't exist should return 404."""
        res = auth_client.get("/api/researchers/9999")
        assert res.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Studies
# ═══════════════════════════════════════════════════════════════════════════════

class TestStudies:
    def test_list_studies_returns_200(self, auth_client):
        """GET /api/studies should return 200 and a list."""
        res = auth_client.get("/api/studies")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_get_study_by_id(self, auth_client):
        """GET /api/studies/1 should return the correct study."""
        res = auth_client.get("/api/studies/1")
        assert res.status_code == 200
        data = res.get_json()
        assert data["study_id"] == 1
        assert data["status"] == "Active"

    def test_get_nonexistent_study_returns_404(self, auth_client):
        """Requesting a study that doesn't exist should return 404."""
        res = auth_client.get("/api/studies/9999")
        assert res.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Participants
# ═══════════════════════════════════════════════════════════════════════════════

class TestParticipants:
    def test_list_participants_returns_200(self, auth_client):
        """GET /api/participants should return 200 and a list."""
        res = auth_client.get("/api/participants")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_filter_by_study_id(self, auth_client):
        """GET /api/participants?study_id=1 should filter correctly."""
        res = auth_client.get("/api/participants?study_id=1")
        assert res.status_code == 200
        data = res.get_json()
        assert all(p["study_id"] == 1 for p in data)


# ═══════════════════════════════════════════════════════════════════════════════
# Outcomes
# ═══════════════════════════════════════════════════════════════════════════════

class TestOutcomes:
    def test_list_outcomes_returns_200(self, auth_client):
        """GET /api/outcomes should return 200 and a list."""
        res = auth_client.get("/api/outcomes")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_filter_by_participant_id(self, auth_client):
        """GET /api/outcomes?participant_id=1 should filter correctly."""
        res = auth_client.get("/api/outcomes?participant_id=1")
        assert res.status_code == 200
        data = res.get_json()
        assert all(o["participant_id"] == 1 for o in data)


# ═══════════════════════════════════════════════════════════════════════════════
# Biosamples
# ═══════════════════════════════════════════════════════════════════════════════

class TestBiosamples:
    def test_list_biosamples_returns_200(self, auth_client):
        """GET /api/biosamples should return 200 and a list."""
        res = auth_client.get("/api/biosamples")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)

    def test_filter_by_sample_type(self, auth_client):
        """GET /api/biosamples?sample_type=Blood should filter correctly."""
        res = auth_client.get("/api/biosamples?sample_type=Blood")
        assert res.status_code == 200
        data = res.get_json()
        assert all("Blood" in b["sample_type"] for b in data)


# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

class TestSummary:
    def test_summary_returns_all_sections(self, auth_client):
        """GET /api/summary should return researchers, studies, participants, outcomes, biosamples."""
        res = auth_client.get("/api/summary")
        assert res.status_code == 200
        data = res.get_json()
        assert "researchers"  in data
        assert "studies"      in data
        assert "participants" in data
        assert "outcomes"     in data
        assert "biosamples"   in data
