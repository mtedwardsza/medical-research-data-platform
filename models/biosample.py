"""
models/biosample.py
===================
SQLAlchemy ORM model for the biosamples table.

A Biosample is a biological specimen collected from a Participant
(e.g. Blood, Saliva, Bone Marrow). Each Biosample belongs to one Participant
and is managed by a lab technician.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Biosample(Base):
    """
    Represents a biological specimen collected from a participant.
    Child of Participant.
    """
    __tablename__ = "biosamples"

    # ── Primary Key ───────────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ── Biosample identity ────────────────────────────────────────────────────
    biosample_id = Column(Integer, unique=True, nullable=False, index=True)

    # ── Foreign Key ───────────────────────────────────────────────────────────
    participant_id = Column(
        Integer,
        ForeignKey("participants.participant_id"),
        nullable=False,
        index=True
    )

    # ── Sample details ────────────────────────────────────────────────────────
    sample_type      = Column(String(100), nullable=False)  # e.g. "Blood", "Saliva", "Bone Marrow"
    collection_date  = Column(Date, nullable=False)
    status           = Column(String(50))                   # e.g. "Stored", "Processing", "Discarded"
    storage_location = Column(String(100))                  # e.g. "Freezer A", "Freezer C"

    # ── Measurements ──────────────────────────────────────────────────────────
    # Volume collected in millilitres
    volume_ml = Column(Float)

    # Processing cost in AUD — Numeric(10, 2) matches currency format in raw data
    processing_cost = Column(Numeric(10, 2))

    # ── Quality indicator ─────────────────────────────────────────────────────
    # is_viable: True if sample is still usable for analysis
    is_viable = Column(Boolean, default=True)

    # ── Lab staff ─────────────────────────────────────────────────────────────
    # Name of the technician who collected/processed the sample (stored as string,
    # not a FK — technicians are not modelled as their own entity in this schema)
    lab_technician = Column(String(200))

    # ── Relationships ─────────────────────────────────────────────────────────
    participant = relationship("Participant", back_populates="biosamples")

    def __repr__(self):
        return (
            f"<Biosample {self.biosample_id}: {self.sample_type} "
            f"from participant {self.participant_id} — {self.status}>"
        )
