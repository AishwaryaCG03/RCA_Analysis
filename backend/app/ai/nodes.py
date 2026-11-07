from typing import TypeVar

from langchain_groq import ChatGroq
from pydantic import BaseModel
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.prompts import (
    CAPA_PROMPT,
    EVIDENCE_PROMPT,
    EXTRACTION_PROMPT,
    FISHBONE_PROMPT,
    FIVE_WHYS_PROMPT,
    ROOT_CAUSE_PROMPT,
)
from app.ai.state import RCAState
from app.core.config import get_settings
from app.schemas import (
    CAPAActionPayload,
    EvidenceItemPayload,
    FishboneCategory,
    IncidentDetails,
    RootCauseItem,
    WhyStep,
)

SchemaT = TypeVar("SchemaT", bound=BaseModel)


def _llm() -> ChatGroq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured. Add it to backend/.env before using AI processing.")
    return ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0)


@retry(
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    stop=stop_after_attempt(3),
    reraise=True,
)
def _structured(prompt: str, schema: type[SchemaT]) -> SchemaT:
    # with_structured_output sends the schema to Groq; Pydantic validates the response.
    result = _llm().with_structured_output(schema).invoke(prompt)
    if not isinstance(result, schema):
        result = schema.model_validate(result)
    return result


class FiveWhysOutput(BaseModel):
    steps: list[WhyStep]


class FishboneOutput(BaseModel):
    categories: list[FishboneCategory]


class RootCauseOutput(BaseModel):
    root_causes: list[RootCauseItem]


class EvidenceOutput(BaseModel):
    missing_evidence: list[EvidenceItemPayload]


class CAPAOutput(BaseModel):
    capa_actions: list[CAPAActionPayload]


def extract_incident(state: RCAState) -> RCAState:
    incident = _structured(EXTRACTION_PROMPT.format(text=state["text"]), IncidentDetails)
    return {"incident": incident}


def validate_incident(state: RCAState) -> RCAState:
    warnings = list(state.get("warnings", []))
    required_for_analysis = ("incident_description", "expected_parameter", "actual_parameter")
    missing = [name.replace("_", " ") for name in required_for_analysis if not getattr(state["incident"], name).value]
    if missing:
        warnings.append("The report does not state " + ", ".join(missing) + "; investigation suggestions are limited.")
    return {"warnings": warnings}


def five_whys(state: RCAState) -> RCAState:
    output = _structured(
        FIVE_WHYS_PROMPT.format(
            incident=state["incident"].model_dump(mode="json"), text=state["text"], existing_steps=[]
        ),
        FiveWhysOutput,
    )
    return {"five_whys": output.steps}


def fishbone(state: RCAState) -> RCAState:
    output = _structured(
        FISHBONE_PROMPT.format(incident=state["incident"].model_dump(mode="json"), text=state["text"]),
        FishboneOutput,
    )
    return {"fishbone": output.categories}


def identify_root_causes(state: RCAState) -> RCAState:
    output = _structured(
        ROOT_CAUSE_PROMPT.format(
            incident=state["incident"].model_dump(mode="json"),
            five_whys=[item.model_dump(mode="json") for item in state.get("five_whys", [])],
            fishbone=[item.model_dump(mode="json") for item in state.get("fishbone", [])],
        ),
        RootCauseOutput,
    )
    return {"root_causes": output.root_causes}


def identify_missing_evidence(state: RCAState) -> RCAState:
    output = _structured(
        EVIDENCE_PROMPT.format(
            incident=state["incident"].model_dump(mode="json"),
            root_causes=[item.model_dump(mode="json") for item in state.get("root_causes", [])],
        ),
        EvidenceOutput,
    )
    return {"missing_evidence": output.missing_evidence}


def generate_capa(state: RCAState) -> RCAState:
    output = _structured(
        CAPA_PROMPT.format(
            incident=state["incident"].model_dump(mode="json"),
            root_causes=[item.model_dump(mode="json") for item in state.get("root_causes", [])],
            missing_evidence=[item.model_dump(mode="json") for item in state.get("missing_evidence", [])],
        ),
        CAPAOutput,
    )
    return {"capa_actions": output.capa_actions}


def validate_result(state: RCAState) -> RCAState:
    warnings = list(state.get("warnings", []))
    for cause in state.get("root_causes", []):
        if cause.status == "Confirmed by Investigator":
            cause.status = "Suggested"
            warnings.append("An AI suggestion was reset to Suggested; a human investigator must confirm it.")
    return {"warnings": warnings}


def generate_five_whys(incident: IncidentDetails, text: str, existing_steps: list[WhyStep] | None = None) -> list[WhyStep]:
    output = _structured(
        FIVE_WHYS_PROMPT.format(
            incident=incident.model_dump(mode="json"), text=text, existing_steps=[x.model_dump(mode="json") for x in existing_steps or []]
        ), FiveWhysOutput
    )
    return output.steps


def generate_fishbone(incident: IncidentDetails, text: str) -> list[FishboneCategory]:
    return _structured(FISHBONE_PROMPT.format(incident=incident.model_dump(mode="json"), text=text), FishboneOutput).categories


def generate_root_causes(incident: IncidentDetails, five_whys_steps: list[WhyStep], fishbone_items: list[FishboneCategory]) -> list[RootCauseItem]:
    return _structured(ROOT_CAUSE_PROMPT.format(incident=incident.model_dump(mode="json"), five_whys=[x.model_dump(mode="json") for x in five_whys_steps], fishbone=[x.model_dump(mode="json") for x in fishbone_items]), RootCauseOutput).root_causes


def generate_evidence(incident: IncidentDetails, causes: list[RootCauseItem]) -> list[EvidenceItemPayload]:
    return _structured(EVIDENCE_PROMPT.format(incident=incident.model_dump(mode="json"), root_causes=[x.model_dump(mode="json") for x in causes]), EvidenceOutput).missing_evidence


def generate_capa_actions(incident: IncidentDetails, causes: list[RootCauseItem], evidence: list[EvidenceItemPayload]) -> list[CAPAActionPayload]:
    return _structured(CAPA_PROMPT.format(incident=incident.model_dump(mode="json"), root_causes=[x.model_dump(mode="json") for x in causes], missing_evidence=[x.model_dump(mode="json") for x in evidence]), CAPAOutput).capa_actions
