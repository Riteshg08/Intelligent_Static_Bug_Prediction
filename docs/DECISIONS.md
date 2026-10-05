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

## Scoring and Patterns
- Replaced the logic that hardcoded risk score to 0.95 (High) when high-severity static hotspots/secrets are detected. Now ML probability score is preserved strictly for statistical properties, while `pattern_severity` (none/info/warning/high) represents absolute rules.
- Review Priority Sort Algorithm: Priority sorting should rely first on pattern severity (e.g. High patterns appear first) then break ties using the absolute risk score. This ensures secrets are immediately visible but ML predictions remain accurate.
- File-level aggregation exposed via API calculates max risk score across functions and a **size-weighted mean risk** (weighted by function line counts) to give a better view of overall code quality without skewing from tiny functions.

## Machine Learning & Datasets
- **Deleted Synthetic Data Pipeline**: `dataset/generate_synthetic.py` and models trained on synthetic rules (like `20261002_173859`, etc.) were completely deleted. Training models on rules or random numbers produces perfectly accurate but completely useless predictors. Models must be trained honestly on real code changes to have real predictive validity.
- **Model Promotion Criteria**: A language-specific ML model is only promoted to "active" (production) if its F1 score on the validation holdout strictly beats BOTH the naive majority class baseline AND a naive baseline guessing purely on lines-of-code (`loc_90`).
- **Model Not Trained State**: If models fail to beat simple baselines on real data, they remain in "experimental_fallback" status and are not promoted. The system falls back to a gracefully handled "Model not trained" UI/API state, ensuring users are not misled by unverified model scores.
