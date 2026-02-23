from typing import Dict, Any, List


def track_players_and_ball(video_path: str) -> Dict[str, Any]:
    return {
        "fps": 25,
        "players": [
            {"id": "p1", "team": "home", "positions": [[0.2, 0.3], [0.21, 0.31]]},
            {"id": "p2", "team": "away", "positions": [[0.6, 0.5], [0.61, 0.48]]},
        ],
        "ball": {"positions": [[0.5, 0.5], [0.52, 0.49]]},
    }
