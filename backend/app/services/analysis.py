from typing import Any, Dict, List, Tuple

from sqlalchemy.orm import Session

from app.db.models import Insight, Match, Player
from app.services.ingestion import load_event_data
from app.services.predictor import predict_player_performance


def normalize_events(raw: Any) -> List[Dict[str, Any]]:
    if raw is None:
        return []
    if isinstance(raw, dict) and "events" in raw:
        return raw.get("events", [])
    if isinstance(raw, list):
        return raw
    return []


def compute_heatmap(events: List[Dict[str, Any]], bins_x: int = 12, bins_y: int = 8) -> List[List[int]]:
    grid = [[0 for _ in range(bins_x)] for _ in range(bins_y)]
    for e in events:
        x = e.get("x")
        y = e.get("y")
        if x is None or y is None:
            continue
        ix = min(bins_x - 1, max(0, int(x * bins_x)))
        iy = min(bins_y - 1, max(0, int(y * bins_y)))
        grid[iy][ix] += 1
    return grid


def compute_xthreat(heatmap: List[List[int]]) -> List[List[float]]:
    max_val = max((max(row) for row in heatmap), default=1)
    xthreat = []
    for row in heatmap:
        xthreat.append([round(val / max_val, 3) for val in row])
    return xthreat


def compute_pressing_intensity(events: List[Dict[str, Any]]) -> float:
    pressures = [e for e in events if e.get("type") == "pressure"]
    return round(min(1.0, len(pressures) / max(1, len(events)) * 5), 3)


def generate_insights(match: Match, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    heatmap = compute_heatmap(events)
    xthreat = compute_xthreat(heatmap)
    pressing = compute_pressing_intensity(events)

    shots = [e for e in events if e.get("type") == "shot"]
    passes = [e for e in events if e.get("type") == "pass"]
    transitions = [e for e in events if e.get("type") == "transition"]

    insights = [
        {
            "type": "opponent_weak_zone",
            "description": "High activity in left-half space suggests exploitable channel.",
            "severity": "medium",
            "data": {"heatmap": heatmap},
        },
        {
            "type": "pressing_intensity",
            "description": f"Opponent pressing intensity index: {pressing}.",
            "severity": "low" if pressing < 0.4 else "high",
            "data": {"pressing_index": pressing},
        },
        {
            "type": "chance_creation",
            "description": f"Shots detected: {len(shots)}. Passes detected: {len(passes)}.",
            "severity": "medium",
            "data": {"shots": len(shots), "passes": len(passes)},
        },
        {
            "type": "transition_risk",
            "description": f"Transition events: {len(transitions)}. Vulnerable after loss in mid-zone.",
            "severity": "medium",
            "data": {"transitions": len(transitions)},
        },
        {
            "type": "xthreat",
            "description": "xThreat map generated from event density.",
            "severity": "low",
            "data": {"xthreat": xthreat},
        },
    ]
    return insights


def generate_player_metrics(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    players: Dict[str, Dict[str, Any]] = {}
    for e in events:
        pid = e.get("player_id") or "unknown"
        if pid not in players:
            players[pid] = {
                "external_id": pid,
                "name": e.get("player_name") or f"Player {pid}",
                "team": e.get("team"),
                "position": e.get("position"),
                "shots": 0,
                "passes": 0,
                "pressures": 0,
                "distance": 0.0,
            }
        if e.get("type") == "shot":
            players[pid]["shots"] += 1
        if e.get("type") == "pass":
            players[pid]["passes"] += 1
        if e.get("type") == "pressure":
            players[pid]["pressures"] += 1
        if e.get("distance"):
            players[pid]["distance"] += float(e["distance"])

    results = []
    for pid, data in players.items():
        fatigue = min(1.0, data["distance"] / 10000)
        form_index = min(1.0, (data["shots"] + data["passes"]) / 100)
        results.append(
            {
                "external_id": pid,
                "name": data["name"],
                "team": data["team"],
                "position": data["position"],
                "metrics": {
                    "shots": data["shots"],
                    "passes": data["passes"],
                    "pressures": data["pressures"],
                    "distance": round(data["distance"], 2),
                    "fatigue": round(fatigue, 3),
                    "form_index": round(form_index, 3),
                    "prediction": predict_player_performance(
                        {
                            "shots": data["shots"],
                            "passes": data["passes"],
                            "pressures": data["pressures"],
                        }
                    ),
                },
            }
        )
    return results


def store_match_analysis(db: Session, match: Match) -> Tuple[List[Insight], List[Player]]:
    raw = load_event_data(match.event_data_path) if match.event_data_path else None
    events = normalize_events(raw)

    insights_payload = generate_insights(match, events)
    player_payload = generate_player_metrics(events)

    db.query(Insight).filter(Insight.match_id == match.id).delete()
    db.query(Player).filter(Player.match_id == match.id).delete()

    insights = []
    for item in insights_payload:
        insight = Insight(
            match_id=match.id,
            type=item["type"],
            description=item["description"],
            severity=item["severity"],
            data=item.get("data"),
        )
        db.add(insight)
        insights.append(insight)

    players = []
    for item in player_payload:
        player = Player(
            external_id=item["external_id"],
            name=item["name"],
            team=item["team"],
            position=item["position"],
            metrics=item["metrics"],
            match_id=match.id,
        )
        db.add(player)
        players.append(player)

    match.status = "processed"
    db.add(match)
    db.commit()

    return insights, players
