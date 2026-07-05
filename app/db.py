"""
app/db.py
=========
Database configuration and SQLAlchemy setup.

This module is the SINGLE SOURCE OF TRUTH for the database connection.
All ORM models import Base from here, and all routes import get_db from here.

WHY A SINGLE Base?
    SQLAlchemy needs all models to share the same Base instance so it can
    create/manage all tables together with Base.metadata.create_all().
    If each model had its own Base, the tables wouldn't "know" about each other.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()  # Load DATABASE_URL from .env file

# ── Database URL ──────────────────────────────────────────────────────────────
# Format: postgresql://user:password@host:port/database
# Loaded from environment variable — never hardcode credentials in source code
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/medical_research")

# ── Engine ────────────────────────────────────────────────────────────────────
# The engine manages the connection pool to PostgreSQL.
# pool_pre_ping=True checks the connection health before each use.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ── Session factory ───────────────────────────────────────────────────────────
# SessionLocal is a class — call SessionLocal() to create a new session.
# autocommit=False: changes are only saved when session.commit() is called.
# autoflush=False:  SQLAlchemy won't auto-flush pending changes before queries.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Declarative Base ──────────────────────────────────────────────────────────
# All ORM model classes inherit from Base.
# Base.metadata holds the full schema — used to create/drop all tables.
Base = declarative_base()


# ── Dependency: get_db ────────────────────────────────────────────────────────
def get_db():
    """
    Provides a database session for a single request lifecycle.

    Usage in routes:
        db = next(get_db())
        researchers = db.query(Researcher).all()

    The try/finally ensures the session is always closed after the request,
    even if an exception occurs — preventing connection leaks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
