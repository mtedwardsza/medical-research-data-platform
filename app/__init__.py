"""
app/__init__.py
===============
Flask application factory.

WHY A FACTORY FUNCTION (create_app)?
    Instead of creating the Flask app at module level, we use a factory function.
    This makes the app easier to test (you can create multiple app instances
    with different configs) and avoids circular import issues.

USAGE:
    from app import create_app
    app = create_app()
    app.run()
"""

import os
from flask import Flask
from app.db import engine, Base


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Steps:
    1. Initialise the Flask instance
    2. Configure session secret key
    3. Create all database tables (if they don't exist yet)
    4. Register the API routes Blueprint
    5. Register the Auth Blueprint
    6. Return the configured app
    """
    app = Flask(__name__)

    # ── Session secret key ────────────────────────────────────────────────────
    # Required for Flask's signed session cookie (used by auth).
    # In production this must be a long random string stored in .env
    app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-in-production")

    # ── Create database tables ────────────────────────────────────────────────
    from models.researcher  import Researcher   # noqa: F401
    from models.study       import Study        # noqa: F401
    from models.participant import Participant  # noqa: F401
    from models.outcome     import Outcome      # noqa: F401
    from models.biosample   import Biosample    # noqa: F401

    Base.metadata.create_all(bind=engine)

    # ── Register Blueprints ───────────────────────────────────────────────────
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Auth blueprint — handles /auth/login, /auth/logout, /auth/me
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # ── Root endpoint ─────────────────────────────────────────────────────────
    @app.get("/")
    def index():
        return {"message": "Medical Research Data Platform API", "status": "running", "version": "1.0"}

    return app
