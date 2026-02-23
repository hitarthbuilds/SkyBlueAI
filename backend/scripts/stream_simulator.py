import argparse
import random
import time

import httpx


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--match", default="match-001")
    parser.add_argument("--key", default="")
    parser.add_argument("--rate", type=float, default=1.0)
    args = parser.parse_args()

    headers = {}
    if args.key:
        headers["X-API-Key"] = args.key

    event_types = ["pass", "shot", "pressure", "transition"]
    team_names = ["Man City", "Opponent"]

    counter = 0
    while True:
        payload = {
            "match_id": args.match,
            "timestamp": counter,
            "type": random.choice(event_types),
            "team": random.choice(team_names),
            "player_id": str(random.randint(1, 30)),
            "x": round(random.random(), 3),
            "y": round(random.random(), 3),
            "payload": {"speed": round(random.uniform(1.0, 7.0), 2)},
        }
        res = httpx.post(f"{args.api}/ingest/event", json=payload, headers=headers, timeout=5.0)
        res.raise_for_status()
        counter += 1
        time.sleep(max(0.1, args.rate))


if __name__ == "__main__":
    main()
