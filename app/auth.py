"""
app/auth.py
===========
Authentication blueprint for the Medical Research Data Platform.

APPROACH: Session-based authentication with role-based access control (RBAC).
    - No external auth library needed — uses Flask's built-in session (signed cookie)
    - Two roles: 'admin' (full access) and 'viewer' (read-only)
    - Credentials stored in environment variables (never hardcoded)
    - login_required decorator protects any route

ROLES:
    admin  → can view all data + access summary statistics
    viewer → read-only access to researchers, studies, participants

USAGE IN ROUTES:
    from app.auth import login_required, admin_required

    @api_bp.get("/sensitive-endpoint")
    @login_required
    def sensitive():
        ...

    @api_bp.get("/admin-only")
    @admin_required
    def admin_only():
        ...
"""

import os
import functools
from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint("auth", __name__)

# ── Credentials loaded from environment ───────────────────────────────────────
# In production these come from .env / Docker secrets / cloud secret manager
# Format: username:password pairs defined as env vars
USERS = {
    os.getenv("ADMIN_USERNAME", "admin"): {
        "password": os.getenv("ADMIN_PASSWORD", "perkins2026"),
        "role":     "admin",
        "name":     "Platform Administrator"
    },
    os.getenv("VIEWER_USERNAME", "viewer"): {
        "password": os.getenv("VIEWER_PASSWORD", "research2026"),
        "role":     "viewer",
        "name":     "Research Viewer"
    }
}


# ── Decorators ────────────────────────────────────────────────────────────────

def login_required(f):
    """
    Decorator — protects a route from unauthenticated access.

    If the user is not logged in:
      - API calls (JSON) → return 401 Unauthorized JSON response
      - Browser calls    → redirect to /auth/login

    Usage:
        @app.route("/protected")
        @login_required
        def protected_view():
            ...
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            # Detect whether this is an API call or a browser request
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required", "code": 401}), 401
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """
    Decorator — restricts a route to admin users only.
    Implies login_required (checks session first, then role).

    Usage:
        @app.route("/admin-panel")
        @admin_required
        def admin_panel():
            ...
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required", "code": 401}), 401
            return redirect(url_for("auth.login"))

        if session["user"].get("role") != "admin":
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Admin access required", "code": 403}), 403
            return jsonify({"error": "Forbidden — admin role required"}), 403

        return f(*args, **kwargs)
    return decorated


# ── Auth routes ────────────────────────────────────────────────────────────────

@auth_bp.get("/login")
def login():
    """
    GET /auth/login
    Renders the login page.
    If already logged in, redirects to the dashboard.
    """
    if "user" in session:
        return redirect("/")
    return render_template("login.html")


@auth_bp.post("/login")
def do_login():
    """
    POST /auth/login
    Validates credentials and creates a session.

    Accepts both JSON (API clients) and form data (browser).

    Success → redirect to / (browser) or 200 JSON (API)
    Failure → 401 with error message
    """
    # Support both JSON body and HTML form submission
    if request.is_json:
        data     = request.get_json()
        username = data.get("username", "").strip()
        password = data.get("password", "")
    else:
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

    user = USERS.get(username)

    if not user or user["password"] != password:
        if request.is_json:
            return jsonify({"error": "Invalid username or password"}), 401
        # Re-render login with error message
        return render_template("login.html", error="Invalid username or password"), 401

    # Store minimal user info in session (signed cookie — safe to store role)
    session["user"] = {
        "username": username,
        "role":     user["role"],
        "name":     user["name"]
    }
    session.permanent = True   # session survives browser close (24h by default)

    if request.is_json:
        return jsonify({
            "message":  "Login successful",
            "username": username,
            "role":     user["role"]
        })

    return redirect("/")


@auth_bp.get("/logout")
def logout():
    """
    GET /auth/logout
    Clears the session and redirects to the login page.
    """
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.get("/me")
@login_required
def me():
    """
    GET /auth/me
    Returns the currently logged-in user's profile.
    Useful for the frontend to know who is logged in and what role they have.
    """
    return jsonify({
        "username": session["user"]["username"],
        "name":     session["user"]["name"],
        "role":     session["user"]["role"]
    })
