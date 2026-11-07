from typing import TypedDict

from app.schemas import (
    CAPAActionPayload,
    EvidenceItemPayload,
    FishboneCategory,
    IncidentDetails,
    RootCauseItem,
    WhyStep,
)


class RCAState(TypedDict, total=False):
    text: str
    method: str
    incident: IncidentDetails
    five_whys: list[WhyStep]
    fishbone: list[FishboneCategory]
    root_causes: list[RootCauseItem]
    missing_evidence: list[EvidenceItemPayload]
    capa_actions: list[CAPAActionPayload]
    warnings: list[str]
