# Antigravity Step-by-Step Prompts — Intelligent Static Bug Prediction (Multi-Language)

How to use: paste **Prompt 0 first**, then Prompts 1, 2, 3... **one at a time**. Move on only when the "Done when" check passes. If something fails, paste the error and say "fix this, then re-run the checks."

**Design idea:** the system is built around a **language plugin architecture**. The core pipeline (features → model → API → dashboard) is language-independent. Each language is a small plugin (Tree-sitter grammar + function-node queries + metric settings). Adding a language means adding a plugin, not rewriting the system.

---

## PROMPT 0 — Project context (paste once, at the very start)

```
You are a senior full-stack + ML engineer. We are building "Intelligent Static Bug Prediction": a LANGUAGE-AGNOSTIC system that reads source code in many programming languages WITHOUT executing it, extracts static metrics per function, uses a trained ML model to predict the probability that each function is bug-prone, classifies risk as Low/Medium/High, explains why, and shows results in a web dashboard.

Multi-language design principles:
- Core pipeline is language-independent. Language-specific logic lives ONLY in plugins under static-analysis/sbp_analysis/languages/<language>/.
- Each language plugin provides: file extensions, Tree-sitter grammar, Tree-sitter queries that find function/method nodes, node-type mappings for branches/loops/nesting/parameters/imports, and optional extra metric providers.
- Use a common, language-neutral feature schema so one feature table works for every language. Language is a categorical feature/column.
- Supported at launch: Python, JavaScript, TypeScript, Java, C, C++, C#, Go. Architecture must make adding Rust, PHP, Ruby, Kotlin, Swift, Scala etc. a plugin-only task. Unknown/unsupported file types are skipped and reported, never crash the run.
- Language-specific tools (e.g. Radon for Python) are optional plugins ONLY. Lizard (multi-language) is the primary cross-language metrics tool; Tree-sitter is the primary parser.

Fixed tech stack:
- Python 3.11+ for the platform itself (analysis engine, ML, backend)
- Tree-sitter (py-tree-sitter + language grammar packages), Lizard, optional Radon for Python
- scikit-learn (baselines) + LightGBM (main model), Pandas, NumPy
- FastAPI, SQLAlchemy + Alembic, PostgreSQL, Redis + RQ worker
- Next.js + React + TypeScript + Tailwind CSS
- Docker + docker-compose, GitHub Actions
- pytest, Jest + React Testing Library, Playwright
NOT allowed in MVP: PyTorch/TensorFlow, neural nets, transformers, SVMs.

Repo layout (monorepo):
intelligent-static-bug-prediction/
  frontend/  backend/  ml/  static-analysis/  dataset/  models/  tests/  docs/  scripts/  docker/  .github/workflows/  README.md  PLAN.md  .env.example

Global rules:
1. Work in small steps. After each task, run tests and show me the results.
2. NEVER execute analyzed/uploaded code. Analysis is static parsing only.
3. Results are always probabilities ("likely to contain a defect"), never certainties.
4. Prefer the simplest explainable solution. Do not build features outside the current step.
5. No hard-coded secrets; use environment variables.
6. Write tests alongside code, including per-language tests. Conventional commits (feat:, fix:, test:, docs:, chore:).
7. If something is ambiguous, pick the simplest option, log it in docs/DECISIONS.md, and continue.
8. Never hard-code language-specific assumptions in core code; put them in plugins/config.
9. Finish each step with: what was built, test results, known issues.

Reply only with "Understood" and wait for my first step.
```

---

## PROMPT 1 — Repo setup and planning

```
STEP 1: Project setup.

1. Create the full repo skeleton exactly as listed, with README.md, .gitignore (Python, Node, data files, model caches), and .env.example.
2. Create PLAN.md with a checklist of phases: Setup, Language Plugin Framework, Static Analysis, Dataset, ML, Prediction Engine, Backend, Frontend, Integration, Testing, Deployment/Docs.
3. Create docs/DECISIONS.md and docs/architecture.md. Describe the pipeline: Source Code -> Language Detection -> Parsing (AST via language plugin) -> Feature Extraction -> Static Analysis -> ML Model -> Bug Probability -> Risk Classification + Explanation -> Developer Report.
4. Add docs/adding-a-language.md (stub for now) that will explain how to add a new language plugin.
5. Initialize git with branches main and develop.
6. GitHub Actions workflow: ruff + pytest for Python, lint + tests for frontend (allow empty suites for now).
7. pyproject.toml / requirements per Python package; Makefile with targets: setup, test, lint, train.

Done when: the structure exists, `make test` and `make lint` run without errors, CI file is valid. Show me the tree and results.
```

---

## PROMPT 2 — Language plugin framework and parser

```
STEP 2: Static analysis package, part 1 — language plugins and parsing.

In static-analysis/, create an importable package `sbp_analysis`.

1. Define an abstract `LanguagePlugin` interface with: name, file_extensions, tree-sitter grammar loader, function_query (Tree-sitter query that finds functions/methods/constructors/lambdas-to-ignore), node-type sets for: branch nodes (if/else/switch-case/ternary/catch), loop nodes, nesting-increasing nodes, parameter nodes, local-variable declaration nodes, import/include/require nodes, and comment nodes.
2. Language registry with automatic detection by file extension (and shebang fallback). Unknown file types are skipped and reported in a summary.
3. Implement plugins for: Python, JavaScript, TypeScript (incl. TSX/JSX), Java, C, C++, C#, Go.
4. Parser module: parse any supported file via its plugin. Tolerate syntax errors: Tree-sitter's error-tolerant tree is used where possible; if unusable, skip the file, log a clear warning, and continue. Never crash the whole run. Skip binary, minified, generated, vendored (node_modules, vendor, dist, build) and oversized files by configurable rules.
5. Function extractor (language-neutral output): file_path, language, function_name, qualified_name (Class.method / namespace-aware), start_line, end_line, source_text, content hash. Handle nested functions, async, arrow functions assigned to variables, class methods, constructors, and anonymous functions (ignore or name by assignment).
6. Per-file cache keyed by content hash so a file is never parsed twice in one run.
7. Tests per language using small hand-written snippets: normal file, syntax-error file, nested functions, methods in classes, empty file, unsupported extension.
8. Write docs/adding-a-language.md properly: step-by-step guide to adding a new plugin with an example.

Done when: all tests pass for all 8 languages, a broken file is skipped and logged, and adding a trivial 9th plugin in a test requires no changes to core code. Show me the test output.
```

---

## PROMPT 3 — Language-neutral metrics and features

```
STEP 3: Static analysis package, part 2 — features.

Build the feature extractor driven ENTIRELY by the language plugin's node-type mappings, so the same code works for every language. For every function produce one numeric vector using this common schema:

Complexity: cyclomatic_complexity (Lizard as primary source across languages; cross-check with own tree-based count), loc (non-blank, non-comment), function_length (physical lines), max_nesting_depth, cognitive_complexity_approx (optional simple version)
Structural: num_parameters, num_branches, num_loops, num_local_variables, num_return_statements, ast_node_count, num_call_expressions
Quality: external_import_count (file-level imports/includes), code_smell_count (simple documented language-neutral rules: too many params, too long, too deep, too complex), duplicate_code_ratio (token-hash based within the project, language-neutral), comment_ratio is NOT used (avoid comment-based features)
Meta: language (categorical), is_method (bool)
Optional per-language extras via plugin hook (e.g. Radon maintainability_index for Python). Extras must be optional and must not be required by the model schema unless available for all training languages.

Rules:
- Implement nesting depth, parameter, branch, loop, and return counting via plugin node-type mappings, never with per-language if/else in core code.
- Do NOT use naming-based features or anything needing code execution.
- Historical features module `history_features.py` (num_past_changes, num_past_bugfixes, commit_frequency, num_authors) computed from git history using ONLY commits before a given prediction timestamp (no future information). This is language-independent. Implement but make optional.
- Provide `extract_features(path_or_dir) -> pandas.DataFrame` (one row per function, all languages mixed) and CLI: `python -m sbp_analysis analyze <path> --out features.csv`. Include a run summary: files per language, functions per language, files skipped and why.
- Tests: for EACH supported language, hand-verified snippets with known expected values (e.g. 3 ifs + 1 loop -> expected complexity; 4 nested blocks -> nesting depth 4). Also test that history features never use commits after the cutoff.

Done when: metrics match hand-verified values in all 8 languages and the CLI runs on a real mixed-language folder. Show me the results.
```

---

## PROMPT 4 — Dataset collection (SZZ-style, multi-language)

```
STEP 4: Dataset pipeline in dataset/.

Build scripts to create a labeled function-level bug dataset using an SZZ-style approach, for all supported languages.

1. Config file repos.yaml listing mature, actively maintained open-source repos with issue tracking, GROUPED BY LANGUAGE: 10-30 repos per supported language (start with a smaller pilot set per language). Propose a sensible list and let me edit it.
2. Resumable clone script (skips existing clones).
3. Find bug-fix commits: commit-message keywords (fix, bug, issue #, resolves #, closes #) plus linked issue metadata via GitHub API where available (rate-limit aware, token from env var). Keywords/labels are configurable per repo.
4. SZZ step: for each fix commit, use git blame/history on changed lines to find the bug-introducing commit and the function touched. Use the language plugins to map changed lines to functions. Extract the function code as it was just before the fix -> label buggy=1.
5. Sample an equal-or-larger set of functions never touched by a bug-fix commit in the observation window -> buggy=0.
6. Run the Step 3 feature extractor on every labeled function. Historical features use only commits BEFORE the labeled point in time.
7. Output parquet/CSV with columns: repo, language, file, function, commit, timestamp, label, plus all features.
8. Deduplicate exact and near-duplicate functions (content hash + normalized-token similarity), within and across repos.
9. Split by repository AND time, per language: the most recent history is the held-out test set. Also create a "leave-one-language-out" evaluation split to test cross-language generalization. No random row splits.
10. Script exporting a random sample of 50 labeled functions PER LANGUAGE to markdown for manual label spot-checking.
11. Leakage-check script: no function/near-duplicate appears in more than one split; prints a report. Also print class balance per language.
12. Write docs/dataset.md. Do not commit large raw data.

First run the pipeline on 2 small repos in 2 different languages, show results and label counts, and WAIT for my approval before running on all repos.

Done when: a deduplicated, labeled dataset with splits exists, the leakage check passes, and class counts per language are reported.
```

---

## PROMPT 5 — ML training and evaluation (multi-language)

```
STEP 5: ML pipeline in ml/.

Using the train/val/test files from Step 4, compare two strategies and let the data decide:
  Strategy A: ONE global LightGBM model using all languages, with `language` as a categorical feature.
  Strategy B: ONE model per language, plus a global fallback model for languages with too little data or unsupported languages.

1. Preprocessing: cleaning, missing values, consistent feature order, feature list saved. Consider per-language normalization (e.g. percentile rank of a metric within its language) since metric scales differ across languages; test whether it helps.
2. Baselines per language: (a) always predict majority class, (b) heuristic "flag the top 10% largest functions", (c) Logistic Regression, (d) Random Forest.
3. Main model: LightGBM with class weighting. Try SMOTE only if class weighting is clearly insufficient on validation data; record the comparison.
4. Validation: k-fold CV respecting repo/time boundaries. Modest random search over max_depth, learning_rate, n_estimators.
5. Feature selection via importance analysis; record dropped features.
6. Evaluate on the held-out test set, reported PER LANGUAGE and overall: accuracy (flagged as misleading alone), precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, FP and FN counts. Priority: precision, recall, F1, PR-AUC. False negatives are costlier.
7. Also evaluate cross-language generalization (train on some languages, test on a held-out one) and report how well the global model handles a language it never saw.
8. Choose Low/Medium/High thresholds on validation data per model (start Low < 0.35, Medium 0.35-0.65, High > 0.65, then tune).
9. Model registry: models/<version>/ with model.joblib per model + metadata.json (version, training date, dataset hash, languages covered, feature names/order, metrics per language, thresholds, training percentiles per language, git commit). Add "active model" pointer and a routing rule: language has its own model -> use it; otherwise use global fallback and mark the prediction "lower confidence: language not specifically trained".
10. Write ml/reports/evaluation_<version>.md with tables per language, confusion matrices, feature importance charts, baseline comparisons, and the A vs B decision.
11. Reproducible: fixed seeds, one command `make train`, pytest checks pipeline runs and beats majority baseline.

Done when: the chosen model(s) clearly beat BOTH the majority baseline and the "largest 10%" heuristic on held-out data for each language that has a dedicated model. Any language that fails must be marked "experimental" in the metadata. If overall results are weak, STOP and analyze features/labels before continuing.
```

---

## PROMPT 6 — Prediction engine and explanations

```
STEP 6: Prediction engine.

Create a reusable prediction service importable by backend and CLI.

1. Load the active versioned model registry once. For each function: detect language, route to the right model (dedicated or global fallback), verify feature names/order against metadata.json, apply the same preprocessing as training.
2. Return per function: risk_score (0-1), risk_level (Low/Medium/High using that model's thresholds), model_version, language, confidence_note (e.g. "experimental language" or "fallback model"), and an explanation.
3. Aggregate to file level; document the method in docs/DECISIONS.md (e.g. max and size-weighted mean of function risks).
4. Explanation layer (MVP): combine feature_importances_ with the function's actual values and the language-specific training percentiles from metadata to produce the top 2-3 plain-language reasons, e.g. "High cyclomatic complexity (24, higher than 95% of Java functions)", "Deep nesting (9 levels)", "Large function (220 lines)". Compare against the function's OWN language norms. Wording must be developer-friendly and probabilistic.
5. Put the explainer behind an `Explainer` interface so SHAP can replace it later.
6. Tests: risky vs simple example in at least 3 languages; threshold boundary tests; feature-order mismatch raises a clear error; unsupported language uses fallback and reports lower confidence.

Done when: tests pass and CLI `python -m sbp_predict <path>` prints a ranked, mixed-language risk report:
File: payment_service.java  Language: Java  Risk Score: 82%  Risk Level: High
Potentially bug-prone functions: ...  Main reasons: ...
```

---

## PROMPT 7 — Backend: database and models

```
STEP 7: Backend part 1 — FastAPI project and database.

In backend/:
1. FastAPI app with /api/v1 prefix, config via pydantic-settings, structured JSON logging, /health endpoint.
2. SQLAlchemy models + Alembic migrations: users, projects, files, analysis_runs, extracted_features, predictions, bug_reports, model_versions, feedback. Add a `language` column on files, extracted_features, and predictions, plus `confidence_note` on predictions.
   Relationships: User 1->N Projects; Project 1->N Files and Analysis Runs; File 1->N Extracted Features; Analysis Run 1->N Predictions; Prediction belongs to File and references Model Version; Feedback belongs to Prediction and User; Bug Reports belong to Project.
3. Indexes on project_id, run_id, file_id, language, and (run_id, risk_score).
4. Auth: register + login, password hashing, JWT, current-user dependency.
5. docker-compose services for PostgreSQL and Redis for local dev.
6. Tests with pytest and a test DB: auth flow, models, relationships, unauthorized access rejected.

Done when: `alembic upgrade head` works on a clean DB and auth tests pass.
```

---

## PROMPT 8 — Backend: APIs, upload, and worker

```
STEP 8: Backend part 2 — APIs and background analysis.

1. Upload handling: POST /projects accepts a single source file, or a .zip / .tar.gz of a multi-language project. Validate extension and max size, defend against zip-slip/path traversal and zip bombs, store in isolated per-user/per-project storage OUTSIDE any web-served directory. Optional ClamAV scan hook.
2. Endpoints (JWT required except register/login; users access ONLY their own data):
   - POST /projects, GET /projects (with latest risk summary), DELETE /projects/{id}
   - POST /projects/{id}/analyze -> {"run_id": 552, "status": "queued"}; optional body {"languages": [...]} to restrict languages
   - GET /analysis/{run_id}/status (include per-language file counts)
   - GET /analysis/{run_id}/predictions (paginated, sortable by risk_score, filter by risk_level and language)
   - GET /predictions/{id}/report, GET /predictions/{id}/explanation
   - POST /predictions/{id}/feedback (correct / false_alarm)
   - GET /models/current (auth optional; list languages covered, per-language metrics, and which are "experimental")
   - GET /languages (supported languages and their status)
3. Redis + RQ worker: analysis NEVER runs in the request path. Pipeline: detect language -> parse -> extract features -> predict -> explain -> save. Status: queued -> running -> completed | failed. One file's failure must not stop the others; record per-file errors; partial results available while running. Unsupported files are listed as "skipped: unsupported language".
4. Secrets detection in uploaded code (language-independent patterns): flag file, never log secret values.
5. Rate limiting, Pydantic validation. Record model_version and language on every prediction.
6. Worker in its own container, resource-limited, no network access.
7. Tests for every endpoint: success, validation error, unauthenticated, cross-user access denied. Security test with a malicious archive. Test with a mixed-language sample project.
8. Freeze API contract and export OpenAPI to docs/openapi.json.

Done when: a mixed-language zip can be uploaded, processed by the worker, and a full ranked report is retrievable. Show me a curl walkthrough.
```

---

## PROMPT 9 — Frontend

```
STEP 9: Frontend in frontend/ (Next.js + TypeScript + Tailwind).

Generate a typed API client from docs/openapi.json. Design for usability: the riskiest code must be findable within seconds. Loading, empty, and error states everywhere; responsive and accessible. Persistent note: "Risk scores are probabilities, not guarantees."

Screens:
1. Login / Register
2. Dashboard: projects with High/Medium/Low counts, languages detected, last analysis time
3. Upload Project: drag-and-drop file/zip/tar.gz (Git URL field shown but disabled, "coming soon")
4. Analysis Progress: polling status, files processed per language, skipped files with reasons
5. Prediction Results: ranked table of files/functions, language badge, color-coded risk badges, filters (risk level, language), search, sort, pagination
6. File-level view: file risk, language, functions with metrics
7. Code-level view: function source with syntax highlighting that switches per language, and its score
8. Explanation view: plain-language reasons and metric values vs. norms for that language, plus a visible badge when the prediction is "experimental language" or "fallback model"
9. Feedback buttons: "Real bug" / "False alarm"
10. Model Performance page: active model version, per-language precision/recall/F1/PR-AUC, confusion matrix, experimental flags
11. Historical Analysis: route and placeholder (V2)
12. Export report as JSON

Cache fetched data within a session; avoid redundant calls. Tests: Jest + RTL for key components; Playwright E2E for upload -> progress -> results -> explanation -> feedback using a mixed-language project.

Done when: a user can upload a multi-language project, watch progress, read the report and explanations, and submit feedback with no developer help.
```

---

## PROMPT 10 — Integration

```
STEP 10: Integration.

1. `docker-compose up` starts frontend, backend, worker, Redis, PostgreSQL (models mounted from models/, config from .env).
2. Run the full pipeline end-to-end on at least 2 real open-source repos per supported language that were NOT used in training, plus 2 mixed-language repos. Record analysis time, functions per language, skipped files, crashes.
3. Fix integration bugs (feature mismatch, encodings, timeouts, huge/minified files, empty files, weird extensions).
4. Profile and optimize ONLY measured bottlenecks (content-hash caching, batching, parallel file parsing, DB indexes, pagination).
5. Manually sanity-check the top-ranked functions in 3 repos of different languages; report weaknesses honestly, including languages where results look unreliable.

Done when: the pipeline completes on all unseen repos and docs/integration_report.md exists.
```

---

## PROMPT 11 — Testing and evaluation

```
STEP 11: Complete the test matrix and final evaluation.

Report coverage for: unit tests (plugins, parsers, feature calculators, scoring/banding); a per-language test suite that runs the same conformance tests against every plugin; integration tests (parser -> features -> prediction); API tests for every endpoint; static analyzer validation on hand-verified snippets in every language; ML pipeline reproducibility; held-out model validation per language; end-to-end user journey (Playwright); performance tests on small/medium/large and mixed-language projects; security tests (zip-slip, zip bomb, huge files, auth bypass, cross-user access, rate limiting, confirmation the analyzer never executes code); UI tests.

Write docs/test_report.md with coverage numbers, final ML metrics per language (precision, recall, F1, PR-AUC, confusion matrix), comparison vs both baselines, a table of languages with status (Stable / Experimental / Fallback-only), and known issues by severity. Fix all high-severity issues.

Done when: critical paths are well covered, CI is green, and the report is honest about per-language limitations.
```

---

## PROMPT 12 — Deployment and documentation

```
STEP 12: Deployment and documentation.

1. Finalize Dockerfiles for frontend, backend, worker (healthchecks, resource limits, network-isolated worker, env-only config). Make sure all Tree-sitter grammars are installed in the image.
2. Production docker-compose for a modest cloud VM, with HTTPS/TLS via reverse proxy notes.
3. CI/CD: PRs run lint, type checks, tests; merges to main build Docker images.
4. Docs: README quickstart, docs/user-guide.md, docs/architecture.md (diagrams), docs/api.md, docs/dataset.md, docs/ml.md (model card with per-language data, metrics, limitations), docs/security.md (retention and deletion policy), docs/adding-a-language.md (final version, tested by following it to add one extra language such as Rust or PHP as a demonstration).
5. Demo script docs/demo.md using scripts/sample_project/ (mixed languages).
6. Verify on a clean checkout that following only the README runs the system.

Done when: a new developer can run the system and add a new language using only the docs.
```

---

## OPTIONAL — Version 2 prompts (only after everything above is stable)

```
V2-A: Add SHAP per-prediction explanations behind the Explainer interface with a feature flag.
V2-B: Add Git/GitHub URL project import (clone inside the isolated worker) with size limits and private-repo handling.
V2-C: Add historical analysis: store each run, show risk trends across runs/commits per language.
V2-D: Add a retraining script that merges stored feedback with the dataset, retrains per language, evaluates, and promotes a new model only if it beats the current one.
V2-E: Add three new language plugins (Rust, PHP, Ruby) following docs/adding-a-language.md, including datasets and per-language evaluation; mark them Experimental until they pass the baseline checks.
```

---

## Tips
- Paste **one prompt at a time**. If the agent drifts, reply: "Stay within this step only."
- After Prompts 4 and 5, review label samples and per-language results yourself. Some languages will have fewer bug-fix examples and will stay "Experimental" — that is expected and honest.
- Commit to git after every step.
