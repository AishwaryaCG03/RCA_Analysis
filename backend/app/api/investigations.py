import copy
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.session import get_db
from app.models import CAPAAction, EvidenceItem, IncidentDetail, Investigation, InvestigationMethod, InvestigationReview, RootCause
from app.schemas import AnalysisResult, InvestigationPayload, InvestigationResponse, InvestigationSummary, ReviewRequest

router = APIRouter()


def _investigation_number() -> str:
    return f"RCA-{datetime.utcnow():%Y%m%d-%H%M%S-%f}"[:-3]


def _read_analysis(entity: Investigation) -> AnalysisResult:
    if not entity.incident_detail:
        raise HTTPException(500, "Investigation data is incomplete.")
    data = entity.incident_detail.extracted_data
    # The complete, user-edited aggregate is held on the method row; normalized records support reporting/audit.
    aggregate = next((record.result.get("analysis") for record in entity.methods if record.method == "aggregate"), None)
    if not aggregate:
        aggregate = {"incident": data, "method": entity.method or "five_whys"}
    return AnalysisResult.model_validate(aggregate)


def _response(entity: Investigation) -> InvestigationResponse:
    analysis = _read_analysis(entity)
    return InvestigationResponse(
        id=entity.id, investigation_number=entity.investigation_number, title=entity.title,
        product_name=entity.product_name, batch_number=entity.batch_number, department=entity.department,
        method=entity.method, status=entity.status, created_at=entity.created_at, updated_at=entity.updated_at,
        analysis=analysis, source_type=entity.incident_detail.source_type, source_text=entity.incident_detail.source_text,
    )


def _hydrate(entity: Investigation, payload: InvestigationPayload) -> None:
    analysis = payload.analysis
    incident = analysis.incident
    entity.title = payload.title
    entity.status = payload.status
    entity.product_name = incident.product_name.value
    entity.batch_number = incident.batch_number.value
    entity.department = incident.department.value
    entity.incident_description = incident.incident_description.value
    entity.method = analysis.method
    if not entity.incident_detail:
        entity.incident_detail = IncidentDetail(source_type=payload.source_type, source_text=payload.source_text, extracted_data=incident.model_dump(mode="json"))
    else:
        entity.incident_detail.source_type = payload.source_type
        entity.incident_detail.source_text = payload.source_text
        entity.incident_detail.extracted_data = incident.model_dump(mode="json")
    entity.methods.clear()
    entity.methods.append(InvestigationMethod(method="aggregate", result={"analysis": analysis.model_dump(mode="json")}))
    # A client cannot promote an AI hypothesis to confirmed by simply sending a PUT.
    # Preserve only confirmations created through the explicit review endpoint.
    confirmed_ids = {item.payload.get("id") for item in entity.root_causes if item.status == "Confirmed by Investigator"}
    for item in analysis.root_causes:
        if item.status == "Confirmed by Investigator" and item.id not in confirmed_ids:
            item.status = "Suggested"
    entity.root_causes.clear()
    entity.root_causes.extend(
        RootCause(description=item.description, category=item.category, status=item.status, evidence_strength=item.evidence_strength, payload=item.model_dump(mode="json"))
        for item in analysis.root_causes
    )
    entity.evidence_items.clear()
    entity.evidence_items.extend(
        EvidenceItem(evidence_required=item.evidence_required, priority=item.priority, status=item.status, payload=item.model_dump(mode="json"))
        for item in analysis.missing_evidence
    )
    entity.capa_actions.clear()
    entity.capa_actions.extend(
        CAPAAction(capa_code=item.id, action_type=item.action_type, recommended_action=item.recommended_action,
                   department=item.responsible_department, target_date=item.target_completion_date, status=item.status,
                   payload=item.model_dump(mode="json"))
        for item in analysis.capa_actions
    )


def _fetch(db: Session, investigation_id: str) -> Investigation:
    entity = db.scalar(
        select(Investigation).where(Investigation.id == investigation_id).options(
            selectinload(Investigation.incident_detail), selectinload(Investigation.methods),
            selectinload(Investigation.root_causes), selectinload(Investigation.evidence_items), selectinload(Investigation.capa_actions),
        )
    )
    if not entity:
        raise HTTPException(404, "Investigation not found.")
    return entity


@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create(payload: InvestigationPayload, db: Session = Depends(get_db)):
    entity = Investigation(investigation_number=payload.investigation_number or _investigation_number())
    _hydrate(entity, payload)
    db.add(entity)
    db.commit()
    return _response(_fetch(db, entity.id))


@router.get("", response_model=list[InvestigationSummary])
def list_investigations(db: Session = Depends(get_db)):
    return db.scalars(select(Investigation).order_by(Investigation.updated_at.desc())).all()


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: str, db: Session = Depends(get_db)):
    return _response(_fetch(db, investigation_id))


@router.put("/{investigation_id}", response_model=InvestigationResponse)
def update(investigation_id: str, payload: InvestigationPayload, db: Session = Depends(get_db)):
    entity = _fetch(db, investigation_id)
    if entity.status in {"Approved", "Closed"}:
        raise HTTPException(409, "Approved or closed investigations cannot be edited.")
    _hydrate(entity, payload)
    db.commit()
    return _response(_fetch(db, investigation_id))


@router.post("/{investigation_id}/review", response_model=InvestigationResponse)
def review(investigation_id: str, request: ReviewRequest, x_role: str = Header("investigator"), db: Session = Depends(get_db)):
    entity = _fetch(db, investigation_id)
    if request.action == "approve" and x_role.lower() not in {"qa_approver", "admin"}:
        raise HTTPException(403, "Only a QA approver may approve an investigation.")
    mapping = {"save_draft": "Draft", "submit": "Pending Review", "approve": "Approved", "reject": "Rejected", "return": "Under Investigation"}
    if request.action == "confirm_root_cause":
        if not request.root_cause_id:
            raise HTTPException(422, "root_cause_id is required to confirm a root cause.")
        cause = next((item for item in entity.root_causes if item.payload.get("id") == request.root_cause_id), None)
        if not cause:
            raise HTTPException(404, "Root cause not found.")
        cause.status = "Confirmed by Investigator"
        cause_payload = dict(cause.payload)
        cause_payload["status"] = "Confirmed by Investigator"
        cause.payload = cause_payload
        aggregate = next((item for item in entity.methods if item.method == "aggregate"), None)
        if aggregate:
            result = copy.deepcopy(aggregate.result)
            for root_cause in result["analysis"].get("root_causes", []):
                if root_cause.get("id") == request.root_cause_id:
                    root_cause["status"] = "Confirmed by Investigator"
            aggregate.result = result
        entity.status = "Under Investigation"
    else:
        entity.status = mapping[request.action]
    entity.reviews.append(InvestigationReview(decision=request.action, comments=request.comments))
    db.commit()
    return _response(_fetch(db, investigation_id))


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(investigation_id: str, db: Session = Depends(get_db)):
    entity = _fetch(db, investigation_id)
    if entity.status != "Draft":
        raise HTTPException(409, "Only draft investigations may be deleted.")
    db.delete(entity)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
