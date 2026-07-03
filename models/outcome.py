"""
models/outcome.py
=================
SQLAlchemy ORM model for the outcomes table.

An Outcome is a clinical measurement recorded for a Participant
(e.g. Blood Glucose, Cholesterol, Blood Pressure readings).
Each Outcome belongs to exactly one Participant.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base


class Outcome(Base):
    """
    Represents a single clinical measurement for a participant.
    Child of Participant.
    """
    __tablename__ = "outcomes"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Outcome identity ──────────────────────────────────────────────────────
    outcome_id = Column(Integer, unique=True, nullable=False, index=True)

    # ── Foreign Key ───────────────────────────────────────────────────────────
    participant_id = Column(
        Integer,
        ForeignKey("participants.participant_id"),
        nullable=False,
        index=True
    )

    # ── Measurement details ───────────────────────────────────────────────────
    measurement_type = Column(String(200), nullable=False)   # e.g. "Blood Glucose (fasting)"
    value            = Column(Float)                          # Numeric reading
    unit             = Column(String(50))                     # e.g. "mmol/L", "bpm"
    measurement_date = Column(Date, nullable=False)

    # ── Clinical interpretation ───────────────────────────────────────────────
    # True if the value falls within clinically normal reference range
    within_normal_range = Column(Boolean)

    # Free-text clinician notes (nullable — many rows have no notes)
    notes = Column(Text)

    # ── Relationships ─────────────────────────────────────────────────────────
    participant = relationship("Participant", back_populates="outcomes")

    def __repr__(self):
        return (
            f"<Outcome {self.outcome_id}: {self.measurement_type} "
            f"= {self.value} {self.unit} (participant {self.participant_id})>"
        )
