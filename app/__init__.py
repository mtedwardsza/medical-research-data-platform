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

from flask import Flask
from app.db import engine, Base


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Steps:
    1. Initialise the Flask instance
    2. Create all database tables (if they don't exist yet)
    3. Register the API routes Blueprint
    4. Return the configured app
    """
    app = Flask(__name__)

    # ── Create database tables ────────────────────────────────────────────────
    # Import all models here so SQLAlchemy's Base.metadata knows about them
    # before calling create_all(). Order doesn't matter — SQLAlchemy resolves
    # FK dependencies automatically.
    from models.researcher  import Researcher   # noqa: F401
    from models.study       import Study        # noqa: F401
    from models.participant import Participant  # noqa: F401
    from models.outcome     import Outcome      # noqa: F401
    from models.biosample   import Biosample    # noqa: F401

    Base.metadata.create_all(bind=engine)

    # ── Register Blueprints ───────────────────────────────────────────────────
    # A Blueprint groups related routes. We use one Blueprint for all API routes.
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # ── Health check at root ──────────────────────────────────────────────────
    @app.get("/")
    def index():
        return {"message": "Medical Research Data Platform API", "status": "running", "version": "1.0"}

    return app
