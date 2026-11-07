import uuid
from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.session import Base

JSONType = JSON().with_variant(JSONB, "postgresql")


def uuid_str() -> str:
    return str(uuid.uuid4())


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(50), default="investigator")


class Investigation(Timestamped, Base):
    __tablename__ = "investigations"
    __table_args__ = (Index("ix_investigation_status_updated", "status", "updated_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300), default="Untitled investigation")
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    batch_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    department: Mapped[str | None] = mapped_column(String(128), nullable=True)
    incident_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    method: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="Draft", index=True)
    created_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    incident_detail: Mapped["IncidentDetail | None"] = relationship(back_populates="investigation", cascade="all, delete-orphan", uselist=False)
    methods: Mapped[list["InvestigationMethod"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    root_causes: Mapped[list["RootCause"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    capa_actions: Mapped[list["CAPAAction"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")
    reviews: Mapped[list["InvestigationReview"]] = relationship(back_populates="investigation", cascade="all, delete-orphan")


class IncidentDetail(Base):
    __tablename__ = "incident_details"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), unique=True)
    source_type: Mapped[str] = mapped_column(String(32))
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_data: Mapped[dict] = mapped_column(JSONType, default=dict)
    investigation: Mapped[Investigation] = relationship(back_populates="incident_detail")


class InvestigationMethod(Base):
    __tablename__ = "investigation_methods"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    method: Mapped[str] = mapped_column(String(32))
    result: Mapped[dict] = mapped_column(JSONType, default=dict)
    investigation: Mapped[Investigation] = relationship(back_populates="methods")


class RootCause(Base):
    __tablename__ = "root_causes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="Suggested")
    evidence_strength: Mapped[str] = mapped_column(String(40), default="Insufficient evidence")
    payload: Mapped[dict] = mapped_column(JSONType, default=dict)
    investigation: Mapped[Investigation] = relationship(back_populates="root_causes")


class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    evidence_required: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(24), default="Medium")
    status: Mapped[str] = mapped_column(String(32), default="Pending")
    payload: Mapped[dict] = mapped_column(JSONType, default=dict)
    investigation: Mapped[Investigation] = relationship(back_populates="evidence_items")


class CAPAAction(Base):
    __tablename__ = "capa_actions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    capa_code: Mapped[str] = mapped_column(String(64))
    action_type: Mapped[str] = mapped_column(String(32))
    recommended_action: Mapped[str] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(String(128), nullable=True)
    target_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="Proposed")
    payload: Mapped[dict] = mapped_column(JSONType, default=dict)
    investigation: Mapped[Investigation] = relationship(back_populates="capa_actions")


class InvestigationReview(Timestamped, Base):
    __tablename__ = "investigation_reviews"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    investigation_id: Mapped[str] = mapped_column(ForeignKey("investigations.id", ondelete="CASCADE"), index=True)
    reviewer_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    decision: Mapped[str] = mapped_column(String(40))
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    investigation: Mapped[Investigation] = relationship(back_populates="reviews")
