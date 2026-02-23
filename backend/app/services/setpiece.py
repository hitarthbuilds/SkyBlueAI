import uuid
from typing import Any, Dict


def generate_set_piece(opponent_profile: Any = None) -> Dict[str, Any]:
    routine_id = str(uuid.uuid4())
    animation = {
        "ball": {"start": [0.1, 0.5], "end": [0.85, 0.35]},
        "runners": [
            {"id": "A", "path": [[0.4, 0.2], [0.6, 0.35]]},
            {"id": "B", "path": [[0.5, 0.7], [0.7, 0.55]]},
            {"id": "C", "path": [[0.3, 0.5], [0.5, 0.45]]},
        ],
    }
    return {
        "routine_id": routine_id,
        "description": "Outswinging delivery with near-post decoy and far-post overload.",
        "animation": animation,
    }
