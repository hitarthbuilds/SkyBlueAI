# API

## Health
`GET /health`

## Readiness
`GET /ready`

## Upload Video
`POST /upload/video`
- Form fields: `match_id` (optional), `home_team`, `away_team`, `match_date`
- File: `file`

## Upload Events
`POST /upload/events`
- Form fields: `match_id` (optional), `home_team`, `away_team`, `match_date`
- File: `file`

## Match Analysis
`GET /match/{id}/analysis`

## Live Snapshot
`GET /match/{id}/live`

## Live Events
`GET /match/{id}/events?limit=50`

## Ingest Live Event
`POST /ingest/event`
Payload:
```json
{
  "match_id": "match-001",
  "timestamp": 1234.5,
  "type": "pass",
  "team": "Man City",
  "player_id": "10",
  "x": 0.25,
  "y": 0.45,
  "payload": {}
}
```

## Ingest Live Events (Batch)
`POST /ingest/events`
Payload:
```json
[
  {
    "match_id": "match-001",
    "timestamp": 1234.5,
    "type": "pass"
  }
]
```

## WebSocket Live Stream
`GET /ws/match/{id}`
Message payloads include `event` and `snapshot` data.

## Player Metrics
`GET /player/{id}/metrics`

## Set Piece Simulation
`POST /simulate/setpiece`
Payload:
```json
{
  "match_id": "...",
  "opponent_profile": {
    "shape": "4-4-2"
  }
}
```

## Injury Risk
`POST /injury/risk`
Payload:
```json
{
  "distance": 9800,
  "sprints": 26,
  "load_spike": 0.1
}
```

## Tactical Simulation
`POST /tactical/simulate`
Payload:
```json
{
  "context": "mid-block",
  "opponent_shape": "4-2-3-1"
}
```
