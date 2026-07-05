"""
app.py
======
Entry point for the Medical Research Data Platform API.

This file creates the Flask app using the factory pattern defined in app/__init__.py
and starts the development server.

USAGE:
    # Development (local):
    python app.py

    # Via Docker:
    docker-compose up

    # Production (with gunicorn):
    gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

AVAILABLE ENDPOINTS:
    GET  /                          — API info
    GET  /api/health                — health check
    GET  /api/summary               — platform statistics (dashboard feed)
    GET  /api/researchers           — list researchers  (?department=, ?is_active=)
    GET  /api/researchers/<id>      — researcher detail + studies
    GET  /api/studies               — list studies      (?status=, ?phase=)
    GET  /api/studies/<id>          — study detail + researcher + participant count
    GET  /api/participants          — list participants (?study_id=, ?gender=, ?withdrawn=)
    GET  /api/participants/<id>     — participant detail + outcome/biosample counts
    GET  /api/outcomes              — list outcomes     (?participant_id=, ?measurement_type=)
    GET  /api/biosamples            — list biosamples   (?participant_id=, ?sample_type=, ?is_viable=)
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port      = int(os.getenv("APP_PORT", 5000))
    flask_env = os.getenv("FLASK_ENV", "development")
    debug     = flask_env == "development"

    print(f"\n  Medical Research Data Platform API")
    print(f"  Running on http://0.0.0.0:{port}")
    print(f"  Environment: {flask_env}")
    print(f"  Debug mode:  {debug}\n")

    app.run(host="0.0.0.0", port=port, debug=debug)
