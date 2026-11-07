from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.ai.graph import run_analysis
from app.ai.nodes import (
    extract_incident,
    generate_capa_actions,
    generate_evidence,
    generate_fishbone,
    generate_five_whys,
    generate_root_causes,
)
from app.core.config import get_settings
from app.schemas import (
    AnalysisRequest,
    AnalysisResult,
    CAPARequest,
    EvidenceRequest,
    ExtractionResponse,
    MethodRequest,
    RootCauseRequest,
)
from app.services.documents import DocumentExtractionError, extract_pdf_text

router = APIRouter()


def _ai_error(exc: Exception) -> HTTPException:
    if isinstance(exc, RuntimeError) and "GROQ_API_KEY" in str(exc):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=502, detail="The AI response did not match the required investigation schema. Please retry.")
    return HTTPException(status_code=502, detail="AI processing failed. Check the configured Groq model/key and retry.")


@router.post("/extract", response_model=ExtractionResponse)
async def extract(
    source_type: str = Form(...),
    pasted_text: str | None = Form(None),
    email_subject: str | None = Form(None),
    email_body: str | None = Form(None),
    file: UploadFile | None = File(None),
) -> ExtractionResponse:
    if source_type not in {"pdf", "text", "email"}:
        raise HTTPException(422, "source_type must be pdf, text, or email")
    text = ""
    if source_type == "pdf":
        if not file:
            raise HTTPException(422, "A PDF file is required for PDF input.")
        if file.content_type not in {"application/pdf", "application/x-pdf"} and Path(file.filename or "").suffix.lower() != ".pdf":
            raise HTTPException(415, "Only PDF files are supported.")
        payload = await file.read()
        if len(payload) > get_settings().max_upload_mb * 1024 * 1024:
            raise HTTPException(413, f"PDF exceeds the {get_settings().max_upload_mb} MB upload limit.")
        try:
            text = extract_pdf_text(payload)
        except DocumentExtractionError as exc:
            raise HTTPException(422, str(exc)) from exc
    elif source_type == "text":
        text = (pasted_text or "").strip()
    else:
        text = f"Subject: {(email_subject or '').strip()}\n\n{(email_body or '').strip()}".strip()
    if len(text) < 10:
        raise HTTPException(422, "Please provide at least 10 characters of incident information.")
    if len(text) > 150_000:
        raise HTTPException(413, "Input exceeds the 150,000 character processing limit.")
    try:
        incident = extract_incident({"text": text})["incident"]
    except Exception as exc:
        raise _ai_error(exc) from exc
    return ExtractionResponse(incident=incident, source_type=source_type, extracted_characters=len(text))


@router.post("/analyze", response_model=AnalysisResult)
def analyze(request: AnalysisRequest) -> AnalysisResult:
    try:
        return run_analysis(request.text, request.method, request.incident)
    except Exception as exc:
        raise _ai_error(exc) from exc


@router.post("/five-whys")
def five_whys(request: MethodRequest):
    try:
        return {"five_whys": generate_five_whys(request.incident, request.text, request.existing_steps)}
    except Exception as exc:
        raise _ai_error(exc) from exc


@router.post("/fishbone")
def fishbone(request: MethodRequest):
    try:
        return {"fishbone": generate_fishbone(request.incident, request.text)}
    except Exception as exc:
        raise _ai_error(exc) from exc


@router.post("/root-causes")
def root_causes(request: RootCauseRequest):
    try:
        return {"root_causes": generate_root_causes(request.incident, request.five_whys, request.fishbone)}
    except Exception as exc:
        raise _ai_error(exc) from exc


@router.post("/missing-evidence")
def missing_evidence(request: EvidenceRequest):
    try:
        return {"missing_evidence": generate_evidence(request.incident, request.root_causes)}
    except Exception as exc:
        raise _ai_error(exc) from exc


@router.post("/capa")
def capa(request: CAPARequest):
    try:
        return {"capa_actions": generate_capa_actions(request.incident, request.root_causes, request.missing_evidence)}
    except Exception as exc:
        raise _ai_error(exc) from exc
