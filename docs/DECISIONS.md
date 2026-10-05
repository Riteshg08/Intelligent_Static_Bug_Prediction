# Architectural Decisions

## Pipeline Architecture
1. Source Code
2. Language Detection
3. Parsing (AST via language plugin)
4. Feature Extraction
5. Static Analysis
6. ML Model
7. Bug Probability
8. Risk Classification + Explanation
9. Developer Report

## Other Decisions
- Using language plugins to make the core system language-independent.
- Features are extracted based on node types provided by the language plugins.

## Backend API Adjustments
- Added start_line and end_line to the Prediction database model to support UI features like function range tinting and bug highlighting.
- Configured CORS via FRONTEND_URL environment variable to support frontend origin.
- Added endpoints GET /api/v1/analysis/{run_id}/export and GET /api/v1/analysis/{run_id}/status/languages to meet frontend CORE requirements.
- Ensured ownership checks on POST /api/v1/predictions/{id}/feedback to maintain security.
- Added Pydantic schemas in schemas.py and response models to all endpoints to support generating a precise openapi.json.
