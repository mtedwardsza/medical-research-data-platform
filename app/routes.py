"""
app/routes.py
=============
REST API endpoints for the Medical Research Data Platform.

All routes are grouped under a Flask Blueprint named 'api'.
The Blueprint is registered with the prefix /api in app/__init__.py,
so every route here is accessible at /api/<path>.

ENDPOINTS SUMMARY:
    GET  /api/health                      — API health check
    GET  /api/researchers                 — list all researchers (filterable)
    GET  /api/researchers/<id>            — single researcher + their studies
    GET  /api/studies                     — list all studies (filterable)
    GET  /api/studies/<id>                — single study + participants count
    GET  /api/participants                — list all participants (filterable)
    GET  /api/participants/<id>           — single participant + outcomes + biosamples
    GET  /api/outcomes                    — list outcomes (filterable by participant)
    GET  /api/biosamples                  — list biosamples (filterable by participant)
    GET  /api/summary                     — platform-wide statistics dashboard
"""

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from app.db import SessionLocal
from models.researcher  import Researcher
from models.study       import Study
from models.participant import Participant
from models.outcome     import Outcome
from models.biosample   import Biosample

# ── Blueprint ─────────────────────────────────────────────────────────────────
api_bp = Blueprint("api", __name__)


# ── Helper ────────────────────────────────────────────────────────────────────
def get_db():
    """Open a database session for a request."""
    return SessionLocal()


# ── Health check ──────────────────────────────────────────────────────────────
@api_bp.get("/health")
def health():
    """
    GET /api/health
    Returns API and database connectivity status.
    Used by Docker healthcheck and monitoring tools.
    """
    db = get_db()
    try:
        db.execute(func.now())  # Simple query to verify DB connection
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "database": str(e)}), 500
    finally:
        db.close()


# ── Researchers ───────────────────────────────────────────────────────────────
@api_bp.get("/researchers")
def list_researchers():
    """
    GET /api/researchers
    Returns all researchers.

    Optional query parameters:
        ?department=Oncology     — filter by department (partial match)
        ?is_active=true          — filter active/inactive researchers
        ?limit=50                — max results (default 100)
    """
    db = get_db()
    try:
        query = db.query(Researcher)

        # Filter by department (case-insensitive partial match)
        dept = request.args.get("department")
        if dept:
            query = query.filter(Researcher.department.ilike(f"%{dept}%"))

        # Filter by active status
        is_active = request.args.get("is_active")
        if is_active is not None:
            active_bool = is_active.lower() in ("true", "1", "yes")
            query = query.filter(Researcher.is_active == active_bool)

        limit = int(request.args.get("limit", 100))
        researchers = query.order_by(Researcher.last_name).limit(limit).all()

        return jsonify([{
            "researcher_id": r.researcher_id,
            "title":         r.title,
            "first_name":    r.first_name,
            "last_name":     r.last_name,
            "department":    r.department,
            "email":         r.email,
            "hire_date":     r.hire_date.isoformat() if r.hire_date else None,
            "is_active":     r.is_active,
            "orcid_id":      r.orcid_id
        } for r in researchers])

    finally:
        db.close()


@api_bp.get("/researchers/<int:researcher_id>")
def get_researcher(researcher_id):
    """
    GET /api/researchers/<researcher_id>
    Returns a single researcher plus a list of their studies.
    Returns 404 if the researcher does not exist.
    """
    db = get_db()
    try:
        r = db.query(Researcher).filter(
            Researcher.researcher_id == researcher_id
        ).first()

        if not r:
            return jsonify({"error": f"Researcher {researcher_id} not found"}), 404

        return jsonify({
            "researcher_id": r.researcher_id,
            "title":         r.title,
            "first_name":    r.first_name,
            "last_name":     r.last_name,
            "department":    r.department,
            "email":         r.email,
            "phone":         r.phone,
            "hire_date":     r.hire_date.isoformat() if r.hire_date else None,
            "is_active":     r.is_active,
            "orcid_id":      r.orcid_id,
            "studies": [{
                "study_id":    s.study_id,
                "title":       s.title,
                "phase":       s.phase,
                "status":      s.status,
                "start_date":  s.start_date.isoformat() if s.start_date else None,
            } for s in r.studies]
        })

    finally:
        db.close()


# ── Studies ───────────────────────────────────────────────────────────────────
@api_bp.get("/studies")
def list_studies():
    """
    GET /api/studies
    Returns all clinical studies.

    Optional query parameters:
        ?status=Active           — filter by status (exact match)
        ?phase=Phase+II          — filter by phase
        ?limit=50                — max results (default 100)
    """
    db = get_db()
    try:
        query = db.query(Study)

        status = request.args.get("status")
        if status:
            query = query.filter(Study.status == status)

        phase = request.args.get("phase")
        if phase:
            query = query.filter(Study.phase == phase)

        limit = int(request.args.get("limit", 100))
        studies = query.order_by(Study.start_date.desc()).limit(limit).all()

        return jsonify([{
            "study_id":               s.study_id,
            "title":                  s.title,
            "phase":                  s.phase,
            "status":                 s.status,
            "principal_researcher_id": s.principal_researcher_id,
            "start_date":             s.start_date.isoformat() if s.start_date else None,
            "end_date":               s.end_date.isoformat() if s.end_date else None,
            "target_participants":     s.target_participants,
            "ethics_approved":         s.ethics_approved,
            "budget_aud":             float(s.budget_aud) if s.budget_aud else None
        } for s in studies])

    finally:
        db.close()


@api_bp.get("/studies/<int:study_id>")
def get_study(study_id):
    """
    GET /api/studies/<study_id>
    Returns a single study with its researcher details and participant count.
    """
    db = get_db()
    try:
        s = db.query(Study).filter(Study.study_id == study_id).first()

        if not s:
            return jsonify({"error": f"Study {study_id} not found"}), 404

        participant_count = db.query(func.count(Participant.id)).filter(
            Participant.study_id == study_id
        ).scalar()

        return jsonify({
            "study_id":               s.study_id,
            "title":                  s.title,
            "phase":                  s.phase,
            "status":                 s.status,
            "start_date":             s.start_date.isoformat() if s.start_date else None,
            "end_date":               s.end_date.isoformat() if s.end_date else None,
            "target_participants":     s.target_participants,
            "enrolled_participants":   participant_count,
            "ethics_approved":         s.ethics_approved,
            "budget_aud":             float(s.budget_aud) if s.budget_aud else None,
            "principal_researcher": {
                "researcher_id": s.principal_researcher.researcher_id,
                "name": f"{s.principal_researcher.title} {s.principal_researcher.last_name}",
                "department": s.principal_researcher.department
            } if s.principal_researcher else None
        })

    finally:
        db.close()


# ── Participants ──────────────────────────────────────────────────────────────
@api_bp.get("/participants")
def list_participants():
    """
    GET /api/participants
    Returns all participants.

    Optional query parameters:
        ?study_id=5              — filter by study
        ?gender=Female           — filter by gender
        ?withdrawn=false         — filter by withdrawal status
        ?limit=100               — max results (default 100)
    """
    db = get_db()
    try:
        query = db.query(Participant)

        study_id = request.args.get("study_id")
        if study_id:
            query = query.filter(Participant.study_id == int(study_id))

        gender = request.args.get("gender")
        if gender:
            query = query.filter(Participant.gender == gender)

        withdrawn = request.args.get("withdrawn")
        if withdrawn is not None:
            withdrawn_bool = withdrawn.lower() in ("true", "1", "yes")
            query = query.filter(Participant.withdrawn == withdrawn_bool)

        limit = int(request.args.get("limit", 100))
        participants = query.order_by(Participant.enrolment_date.desc()).limit(limit).all()

        return jsonify([{
            "participant_id":    p.participant_id,
            "study_id":          p.study_id,
            "first_name":        p.first_name,
            "last_name":         p.last_name,
            "age":               p.age,
            "gender":            p.gender,
            "postcode":          p.postcode,
            "primary_condition": p.primary_condition,
            "enrolment_date":    p.enrolment_date.isoformat() if p.enrolment_date else None,
            "consent_given":     p.consent_given,
            "withdrawn":         p.withdrawn
        } for p in participants])

    finally:
        db.close()


@api_bp.get("/participants/<int:participant_id>")
def get_participant(participant_id):
    """
    GET /api/participants/<participant_id>
    Returns a single participant with their outcomes and biosample counts.
    """
    db = get_db()
    try:
        p = db.query(Participant).filter(
            Participant.participant_id == participant_id
        ).first()

        if not p:
            return jsonify({"error": f"Participant {participant_id} not found"}), 404

        outcomes_count   = db.query(func.count(Outcome.id)).filter(
            Outcome.participant_id == participant_id).scalar()
        biosamples_count = db.query(func.count(Biosample.id)).filter(
            Biosample.participant_id == participant_id).scalar()

        return jsonify({
            "participant_id":    p.participant_id,
            "study_id":          p.study_id,
            "first_name":        p.first_name,
            "last_name":         p.last_name,
            "age":               p.age,
            "gender":            p.gender,
            "postcode":          p.postcode,
            "primary_condition": p.primary_condition,
            "enrolment_date":    p.enrolment_date.isoformat() if p.enrolment_date else None,
            "consent_given":     p.consent_given,
            "withdrawn":         p.withdrawn,
            "outcomes_count":    outcomes_count,
            "biosamples_count":  biosamples_count
        })

    finally:
        db.close()


# ── Outcomes ──────────────────────────────────────────────────────────────────
@api_bp.get("/outcomes")
def list_outcomes():
    """
    GET /api/outcomes
    Returns clinical measurement outcomes.

    Optional query parameters:
        ?participant_id=101      — filter by participant
        ?measurement_type=Blood+Glucose — filter by type (partial match)
        ?limit=100               — max results (default 100)
    """
    db = get_db()
    try:
        query = db.query(Outcome)

        participant_id = request.args.get("participant_id")
        if participant_id:
            query = query.filter(Outcome.participant_id == int(participant_id))

        mtype = request.args.get("measurement_type")
        if mtype:
            query = query.filter(Outcome.measurement_type.ilike(f"%{mtype}%"))

        limit = int(request.args.get("limit", 100))
        outcomes = query.order_by(Outcome.measurement_date.desc()).limit(limit).all()

        return jsonify([{
            "outcome_id":           o.outcome_id,
            "participant_id":       o.participant_id,
            "measurement_type":     o.measurement_type,
            "value":                o.value,
            "unit":                 o.unit,
            "measurement_date":     o.measurement_date.isoformat() if o.measurement_date else None,
            "within_normal_range":  o.within_normal_range,
            "notes":                o.notes
        } for o in outcomes])

    finally:
        db.close()


# ── Biosamples ────────────────────────────────────────────────────────────────
@api_bp.get("/biosamples")
def list_biosamples():
    """
    GET /api/biosamples
    Returns biological samples.

    Optional query parameters:
        ?participant_id=101      — filter by participant
        ?sample_type=Blood       — filter by sample type
        ?is_viable=true          — filter viable samples
        ?limit=100               — max results (default 100)
    """
    db = get_db()
    try:
        query = db.query(Biosample)

        participant_id = request.args.get("participant_id")
        if participant_id:
            query = query.filter(Biosample.participant_id == int(participant_id))

        sample_type = request.args.get("sample_type")
        if sample_type:
            query = query.filter(Biosample.sample_type.ilike(f"%{sample_type}%"))

        is_viable = request.args.get("is_viable")
        if is_viable is not None:
            viable_bool = is_viable.lower() in ("true", "1", "yes")
            query = query.filter(Biosample.is_viable == viable_bool)

        limit = int(request.args.get("limit", 100))
        biosamples = query.order_by(Biosample.collection_date.desc()).limit(limit).all()

        return jsonify([{
            "biosample_id":      b.biosample_id,
            "participant_id":    b.participant_id,
            "sample_type":       b.sample_type,
            "collection_date":   b.collection_date.isoformat() if b.collection_date else None,
            "status":            b.status,
            "storage_location":  b.storage_location,
            "volume_ml":         b.volume_ml,
            "processing_cost":   float(b.processing_cost) if b.processing_cost else None,
            "is_viable":         b.is_viable,
            "lab_technician":    b.lab_technician
        } for b in biosamples])

    finally:
        db.close()


# ── Summary / Dashboard stats ─────────────────────────────────────────────────
@api_bp.get("/summary")
def summary():
    """
    GET /api/summary
    Returns platform-wide aggregate statistics.
    This endpoint feeds the dashboard (US-05).

    Returns counts, averages, and breakdowns across all entities.
    """
    db = get_db()
    try:
        # Record counts
        total_researchers  = db.query(func.count(Researcher.id)).scalar()
        active_researchers = db.query(func.count(Researcher.id)).filter(
            Researcher.is_active == True).scalar()                             # noqa: E712
        total_studies      = db.query(func.count(Study.id)).scalar()
        total_participants = db.query(func.count(Participant.id)).scalar()
        total_outcomes     = db.query(func.count(Outcome.id)).scalar()
        total_biosamples   = db.query(func.count(Biosample.id)).scalar()

        # Participants: withdrawn vs active
        withdrawn = db.query(func.count(Participant.id)).filter(
            Participant.withdrawn == True).scalar()                             # noqa: E712

        # Studies by status
        studies_by_status = db.query(
            Study.status, func.count(Study.id)
        ).group_by(Study.status).all()

        # Average participant age
        avg_age = db.query(func.avg(Participant.age)).scalar()

        # Outcomes: normal range ratio
        normal_outcomes = db.query(func.count(Outcome.id)).filter(
            Outcome.within_normal_range == True).scalar()                      # noqa: E712

        # Viable biosamples ratio
        viable_biosamples = db.query(func.count(Biosample.id)).filter(
            Biosample.is_viable == True).scalar()                              # noqa: E712

        return jsonify({
            "researchers": {
                "total":  total_researchers,
                "active": active_researchers,
            },
            "studies": {
                "total":     total_studies,
                "by_status": {status: count for status, count in studies_by_status}
            },
            "participants": {
                "total":         total_participants,
                "active":        total_participants - withdrawn,
                "withdrawn":     withdrawn,
                "average_age":   round(float(avg_age), 1) if avg_age else None
            },
            "outcomes": {
                "total":              total_outcomes,
                "within_normal_range": normal_outcomes,
                "abnormal":           total_outcomes - normal_outcomes
            },
            "biosamples": {
                "total":    total_biosamples,
                "viable":   viable_biosamples,
                "discarded": total_biosamples - viable_biosamples
            }
        })

    finally:
        db.close()
