# Data Contracts

## Event Data
The MVP expects event data with normalized coordinates (0-1) and standard event types.

```json
{
  "events": [
    {
      "type": "pass",
      "x": 0.25,
      "y": 0.45,
      "team": "Man City",
      "player_id": "10",
      "player_name": "Kevin",
      "distance": 10.1
    }
  ]
}
```

Supported `type` values: `pass`, `shot`, `pressure`, `transition`.

## Player Metrics Output
```json
{
  "id": "10",
  "name": "Kevin",
  "team": "Man City",
  "metrics": {
    "shots": 0,
    "passes": 2,
    "pressures": 0,
    "distance": 22.5,
    "fatigue": 0.002,
    "form_index": 0.02
  }
}
```
