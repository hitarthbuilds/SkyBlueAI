# ML/CV Notes

This MVP uses deterministic heuristics in `app/services/analysis.py`. To upgrade:

## CV Tracking
- Replace with YOLOv8/Detectron2 for player/ball detection.
- Implement team assignment via kit color clustering.
- Export XY trajectories into the event schema.

## Prediction Models
- Performance: gradient boosting or sequence model over event + tracking inputs.
- Injury: risk model using workload, spikes, and historical injuries.
- Tactical: RL simulation for policy suggestions.

## Model Interfaces
Use the functions in `app/services` as entry points to integrate your models.
