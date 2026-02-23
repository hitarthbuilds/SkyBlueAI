from typing import Dict, Any


def predict_player_performance(metrics: Dict[str, Any]) -> Dict[str, Any]:
    xg = round(min(1.0, metrics.get("shots", 0) * 0.12), 3)
    xa = round(min(1.0, metrics.get("passes", 0) * 0.01), 3)
    defensive = round(min(1.0, metrics.get("pressures", 0) * 0.05), 3)
    return {
        "xg": xg,
        "xa": xa,
        "def_actions": defensive,
        "expected_rating": round(6.0 + xg + xa + defensive, 2),
    }
