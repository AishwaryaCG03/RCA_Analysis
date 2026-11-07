from fastapi.testclient import TestClient

from app.main import app


def source_field(value=None):
    return {"value": value, "basis": "source_fact" if value else "unavailable", "source": None}


def incident():
    values = {
        "deviation_id": "DEV-2026-102", "product_name": "Paracetamol API", "batch_number": "BATCH-102",
        "department": "Manufacturing", "incident_title": "Temperature deviation",
        "incident_description": "Temperature reached 75°C; the specified operating temperature was 60°C.",
        "expected_parameter": "60°C", "actual_parameter": "75°C",
    }
    keys = ["deviation_id", "product_name", "api_name", "batch_number", "manufacturing_date", "incident_date", "department", "equipment_id", "process_stage", "incident_title", "incident_description", "expected_parameter", "actual_parameter", "specification_limits", "immediate_actions", "reported_impact"]
    data = {key: source_field(values.get(key)) for key in keys}
    data.update({"supporting_evidence": [], "extraction_notes": []})
    return data


def payload():
    incident_data = incident()
    return {
        "title": "Paracetamol temperature deviation", "status": "Draft", "source_type": "text",
        "source_text": incident_data["incident_description"]["value"],
        "analysis": {
            "incident": incident_data, "method": "five_whys", "five_whys": [], "fishbone": [],
            "root_causes": [{"id": "RC-1", "description": "Cooling system performance requires investigation", "explanation": "No maintenance record is provided.", "category": "Machine", "supporting_evidence": [], "missing_evidence": ["Maintenance history"], "evidence_strength": "Insufficient evidence", "status": "Suggested"}],
            "missing_evidence": [{"id": "EV-1", "evidence_required": "Cooling-system maintenance history", "reason": "Needed to investigate the machine hypothesis.", "related_root_cause_ids": ["RC-1"], "suggested_record": "Preventive maintenance log", "priority": "High", "status": "Pending"}],
            "capa_actions": [{"id": "CAPA-1", "action_type": "Correction", "recommended_action": "Assess the affected batch.", "reason": "Immediate containment pending qualified assessment.", "related_root_cause_ids": [], "priority": "High", "responsible_department": "Quality", "target_completion_date": None, "status": "Proposed"}],
            "warnings": [],
        },
    }


def test_health_and_investigation_persistence():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        created = client.post("/api/v1/investigations", json=payload())
        assert created.status_code == 201, created.text
        record = created.json()
        fetched = client.get(f"/api/v1/investigations/{record['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["analysis"]["root_causes"][0]["status"] == "Suggested"
        forbidden = client.post(
            f"/api/v1/investigations/{record['id']}/review",
            json={"action": "approve"}, headers={"X-Role": "investigator"},
        )
        assert forbidden.status_code == 403
        confirmed = client.post(
            f"/api/v1/investigations/{record['id']}/review",
            json={"action": "confirm_root_cause", "root_cause_id": "RC-1"},
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["analysis"]["root_causes"][0]["status"] == "Confirmed by Investigator"
        listed = client.get("/api/v1/investigations")
        assert any(item["id"] == record["id"] for item in listed.json())
