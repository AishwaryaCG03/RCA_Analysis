from langgraph.graph import END, START, StateGraph

from app.ai.nodes import (
    extract_incident,
    five_whys,
    fishbone,
    generate_capa,
    identify_missing_evidence,
    identify_root_causes,
    validate_incident,
    validate_result,
)
from app.ai.state import RCAState
from app.schemas import AnalysisResult


def route_method(state: RCAState) -> str:
    return "five_whys" if state.get("method") == "five_whys" else "fishbone"


def route_input(state: RCAState) -> str:
    return "validate_incident" if state.get("incident") else "extract_incident"


def build_rca_graph():
    graph = StateGraph(RCAState)
    graph.add_node("extract_incident", extract_incident)
    graph.add_node("validate_incident", validate_incident)
    graph.add_node("five_whys", five_whys)
    graph.add_node("fishbone", fishbone)
    graph.add_node("identify_root_causes", identify_root_causes)
    graph.add_node("identify_missing_evidence", identify_missing_evidence)
    graph.add_node("generate_capa", generate_capa)
    graph.add_node("validate_result", validate_result)
    graph.add_conditional_edges(START, route_input, {"extract_incident": "extract_incident", "validate_incident": "validate_incident"})
    graph.add_edge("extract_incident", "validate_incident")
    graph.add_conditional_edges("validate_incident", route_method, {"five_whys": "five_whys", "fishbone": "fishbone"})
    graph.add_edge("five_whys", "identify_root_causes")
    graph.add_edge("fishbone", "identify_root_causes")
    graph.add_edge("identify_root_causes", "identify_missing_evidence")
    graph.add_edge("identify_missing_evidence", "generate_capa")
    graph.add_edge("generate_capa", "validate_result")
    graph.add_edge("validate_result", END)
    return graph.compile()


rca_graph = build_rca_graph()


def run_analysis(text: str, method: str, incident=None) -> AnalysisResult:
    initial: RCAState = {"text": text, "method": method, "warnings": []}
    if incident is not None:
        initial["incident"] = incident
    result = rca_graph.invoke(initial)
    return AnalysisResult(
        incident=result["incident"], method=method, five_whys=result.get("five_whys", []),
        fishbone=result.get("fishbone", []), root_causes=result.get("root_causes", []),
        missing_evidence=result.get("missing_evidence", []), capa_actions=result.get("capa_actions", []),
        warnings=result.get("warnings", []),
    )
