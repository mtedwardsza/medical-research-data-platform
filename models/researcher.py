"""
models/researcher.py
====================
SQLAlchemy ORM model for the researchers table.

WHY ORM (Object-Relational Mapping):
    Instead of writing raw SQL like:
        INSERT INTO researchers (first_name, last_name, ...) VALUES (...)
    SQLAlchemy lets you work with Python objects:
        r = Researcher(first_name="Jane", last_name="Smith", ...)
        db.session.add(r)
    This makes the code cleaner, safer (no SQL injection), and easier to test.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date
from sqlalchemy.orm import relationship
from app.db import Base


class Researcher(Base):
    """
    Represents a research staff member at the institute.
    Parent table — Studies reference this via principal_researcher_id.
    """
    __tablename__ = "researchers"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Identity fields ───────────────────────────────────────────────────────
    researcher_id = Column(Integer, unique=True, nullable=False, index=True)
    title         = Column(String(20))
    first_name    = Column(String(100))
    last_name     = Column(String(100), nullable=False)
    department    = Column(String(100), nullable=False)

    # ── Contact ───────────────────────────────────────────────────────────────
    email         = Column(String(200), unique=True)
    phone         = Column(String(50))

    # ── Employment ────────────────────────────────────────────────────────────
    hire_date     = Column(Date)
    is_active     = Column(Boolean, default=True)

    # ── External identifier ───────────────────────────────────────────────────
    # ORCID: Open Researcher and Contributor ID — unique identifier for researchers
    orcid_id      = Column(String(50))

    # ── Relationships ─────────────────────────────────────────────────────────
    # One researcher can lead many studies
    studies = relationship("Study", back_populates="principal_researcher")

    def __repr__(self):
        return f"<Researcher {self.researcher_id}: {self.title} {self.last_name}>"
