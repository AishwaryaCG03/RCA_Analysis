from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Method = Literal["five_whys", "fishbone"]
InvestigationStatus = Literal["Draft", "Under Investigation", "Pending Review", "Approved", "Rejected", "Closed"]


class SourceReference(BaseModel):
    page_number: int | None = None
    excerpt: str | None = None


class SourcedField(BaseModel):
    value: str | None = None
    basis: Literal["source_fact", "inference", "unavailable"] = "unavailable"
    source: SourceReference | None = None


class IncidentDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deviation_id: SourcedField = Field(default_factory=SourcedField)
    product_name: SourcedField = Field(default_factory=SourcedField)
    api_name: SourcedField = Field(default_factory=SourcedField)
    batch_number: SourcedField = Field(default_factory=SourcedField)
    manufacturing_date: SourcedField = Field(default_factory=SourcedField)
    incident_date: SourcedField = Field(default_factory=SourcedField)
    department: SourcedField = Field(default_factory=SourcedField)
    equipment_id: SourcedField = Field(default_factory=SourcedField)
    process_stage: SourcedField = Field(default_factory=SourcedField)
    incident_title: SourcedField = Field(default_factory=SourcedField)
    incident_description: SourcedField = Field(default_factory=SourcedField)
    expected_parameter: SourcedField = Field(default_factory=SourcedField)
    actual_parameter: SourcedField = Field(default_factory=SourcedField)
    specification_limits: SourcedField = Field(default_factory=SourcedField)
    immediate_actions: SourcedField = Field(default_factory=SourcedField)
    reported_impact: SourcedField = Field(default_factory=SourcedField)
    supporting_evidence: list[SourcedField] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)


class ExtractionResponse(BaseModel):
    incident: IncidentDetails
    source_type: Literal["pdf", "text", "email"]
    extracted_characters: int
    warnings: list[str] = Field(default_factory=list)


class WhyStep(BaseModel):
    level: int = Field(ge=1, le=5)
    question: str
    suggested_answer: str | None = None
    rationale: str
    evidence: list[SourceReference] = Field(default_factory=list)
    needs_further_investigation: bool = True
    investigator_decision: Literal["Proposed", "Confirmed", "Rejected"] = "Proposed"


class FishboneFactor(BaseModel):
    id: str
    factor: str
    rationale: str
    supporting_evidence: list[SourceReference] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    status: Literal["Suggested", "Under Investigation", "Evidence Supported", "Rejected"] = "Suggested"


class FishboneCategory(BaseModel):
    category: Literal["Man", "Machine", "Method", "Material", "Measurement", "Environment"]
    factors: list[FishboneFactor] = Field(default_factory=list)


class RootCauseItem(BaseModel):
    id: str
    description: str
    explanation: str
    category: str
    supporting_evidence: list[SourceReference] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    evidence_strength: Literal["Documented support", "Partial support", "Insufficient evidence"]
    status: Literal["Suggested", "Under Investigation", "Evidence Supported", "Confirmed by Investigator", "Rejected"] = "Suggested"


class EvidenceItemPayload(BaseModel):
    id: str
    evidence_required: str
    reason: str
    related_root_cause_ids: list[str] = Field(default_factory=list)
    suggested_record: str
    priority: Literal["High", "Medium", "Low"]
    status: Literal["Pending", "Received", "Reviewed", "Not Applicable"] = "Pending"


class CAPAActionPayload(BaseModel):
    id: str
    action_type: Literal["Correction", "Corrective Action", "Preventive Action"]
    recommended_action: str
    reason: str
    related_root_cause_ids: list[str] = Field(default_factory=list)
    priority: Literal["High", "Medium", "Low"]
    responsible_department: str | None = None
    target_completion_date: date | None = None
    status: Literal["Proposed", "In Progress", "Completed", "Rejected"] = "Proposed"


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=10, max_length=150_000)
    method: Method
    incident: IncidentDetails | None = None


class AnalysisResult(BaseModel):
    incident: IncidentDetails
    method: Method
    five_whys: list[WhyStep] = Field(default_factory=list)
    fishbone: list[FishboneCategory] = Field(default_factory=list)
    root_causes: list[RootCauseItem] = Field(default_factory=list)
    missing_evidence: list[EvidenceItemPayload] = Field(default_factory=list)
    capa_actions: list[CAPAActionPayload] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class MethodRequest(BaseModel):
    incident: IncidentDetails
    text: str = Field(min_length=10, max_length=150_000)
    existing_steps: list[WhyStep] = Field(default_factory=list)


class RootCauseRequest(BaseModel):
    incident: IncidentDetails
    five_whys: list[WhyStep] = Field(default_factory=list)
    fishbone: list[FishboneCategory] = Field(default_factory=list)


class EvidenceRequest(BaseModel):
    incident: IncidentDetails
    root_causes: list[RootCauseItem] = Field(default_factory=list)


class CAPARequest(BaseModel):
    incident: IncidentDetails
    root_causes: list[RootCauseItem] = Field(default_factory=list)
    missing_evidence: list[EvidenceItemPayload] = Field(default_factory=list)


class InvestigationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    investigation_number: str | None = None
    title: str = Field(min_length=1, max_length=300)
    status: InvestigationStatus = "Draft"
    source_type: Literal["pdf", "text", "email"] = "text"
    source_text: str | None = None
    analysis: AnalysisResult


class InvestigationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    investigation_number: str
    title: str
    product_name: str | None
    batch_number: str | None
    department: str | None
    method: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class InvestigationResponse(InvestigationSummary):
    analysis: AnalysisResult
    source_type: str
    source_text: str | None = None


class ReviewRequest(BaseModel):
    action: Literal["save_draft", "submit", "confirm_root_cause", "approve", "reject", "return"]
    comments: str | None = Field(default=None, max_length=3000)
    root_cause_id: str | None = None
