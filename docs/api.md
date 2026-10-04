# API Documentation

## Auth
- `POST /api/v1/auth/register`: Register user.
- `POST /api/v1/auth/login`: Login for token.

## Projects & Analysis
- `GET /api/v1/projects`: List user projects.
- `POST /api/v1/projects`: Upload a project zip.
- `POST /api/v1/projects/{id}/analyze`: Start analysis.
- `GET /api/v1/analysis/{run_id}/status`: Get run status.

## Viewer & Predictions
- `GET /api/v1/analysis/{run_id}/predictions`: Get all predictions for a run.
- `GET /api/v1/analysis/{run_id}/files`: Get all files for a run, with risk counts and max risk score.
- `GET /api/v1/files/{file_id}/source`: Get full file source code.
- `GET /api/v1/files/{file_id}/annotations?run_id=`: Get function ranges and hotspots for a file.
- `GET /api/v1/predictions/{id}/report`: Get full prediction report, explanation, and related hotspots.
- `POST /api/v1/predictions/{id}/feedback`: Submit feedback on a prediction.
