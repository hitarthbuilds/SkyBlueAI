from typing import Dict, Any


def compute_injury_risk(workload: Dict[str, Any]) -> Dict[str, Any]:
    distance = float(workload.get("distance", 0))
    sprints = float(workload.get("sprints", 0))
    load_spike = float(workload.get("load_spike", 0))

    score = min(1.0, (distance / 12000) + (sprints / 40) + load_spike)
    if score < 0.4:
        status = "green"
    elif score < 0.7:
        status = "amber"
    else:
        status = "red"

    return {
        "risk_score": round(score, 3),
        "status": status,
        "recommendation": "Reduce high-speed load for 48h" if status != "green" else "Normal load",
    }
