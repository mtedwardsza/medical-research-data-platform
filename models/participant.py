"""
models/participant.py
=====================
SQLAlchemy ORM model for the participants table.

A Participant is a person enrolled in a Study.
They can have many Outcomes measured and many Biosamples collected.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Participant(Base):
    """
    Represents a person enrolled in a clinical study.
    Child of Study, parent of Outcome and Biosample.
    """
    __tablename__ = "participants"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Participant identity ───────────────────────────────────────────────────
    participant_id = Column(Integer, unique=True, nullable=False, index=True)

    # ── Foreign Key ───────────────────────────────────────────────────────────
    study_id = Column(
        Integer,
        ForeignKey("studies.study_id"),
        nullable=False,
        index=True
    )

    # ── Demographics ──────────────────────────────────────────────────────────
    first_name = Column(String(100))
    last_name  = Column(String(100))
    age        = Column(Integer)
    gender     = Column(String(20))    # Standardised: Male / Female / Non-binary
    postcode   = Column(String(10))

    # ── Clinical info ─────────────────────────────────────────────────────────
    primary_condition = Column(String(100))
    enrolment_date    = Column(Date, nullable=False)

    # ── Consent & status ──────────────────────────────────────────────────────
    # consent_given must be True for active participants (business rule)
    consent_given = Column(Boolean, nullable=False, default=True)
    withdrawn     = Column(Boolean, default=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    study      = relationship("Study", back_populates="participants")
    outcomes   = relationship("Outcome", back_populates="participant")
    biosamples = relationship("Biosample", back_populates="participant")

    def __repr__(self):
        return f"<Participant {self.participant_id}: {self.last_name}, {self.first_name}>"
