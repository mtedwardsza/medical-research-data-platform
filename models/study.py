"""
models/study.py
===============
SQLAlchemy ORM model for the studies table.

A Study is a clinical trial. It belongs to one Researcher (principal investigator)
and has many Participants enrolled in it.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Study(Base):
    """
    Represents a clinical trial or research study.
    Child of Researcher, parent of Participant.
    """
    __tablename__ = "studies"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Study identity ────────────────────────────────────────────────────────
    study_id = Column(Integer, unique=True, nullable=False, index=True)
    title    = Column(String(500), nullable=False)
    phase    = Column(String(20))    # Phase I, II, III, IV
    status   = Column(String(50))    # Active, Completed, Paused, etc.

    # ── Foreign Key ───────────────────────────────────────────────────────────
    # Links to the researcher who leads this study
    principal_researcher_id = Column(
        Integer,
        ForeignKey("researchers.researcher_id"),
        nullable=False,
        index=True
    )

    # ── Timeline ──────────────────────────────────────────────────────────────
    start_date = Column(Date, nullable=False)
    end_date   = Column(Date)    # Nullable — ongoing studies have no end date yet

    # ── Study details ─────────────────────────────────────────────────────────
    target_participants = Column(Integer)
    ethics_approved     = Column(Boolean, default=False)

    # ── Budget ────────────────────────────────────────────────────────────────
    # Numeric(12, 2) = up to 12 digits total, 2 decimal places — suitable for AUD amounts
    budget_aud = Column(Numeric(12, 2))

    # ── Relationships ─────────────────────────────────────────────────────────
    principal_researcher = relationship("Researcher", back_populates="studies")
    participants         = relationship("Participant", back_populates="study")

    def __repr__(self):
        return f"<Study {self.study_id}: {self.title[:40]}...>"
