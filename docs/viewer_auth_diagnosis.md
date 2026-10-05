# Code Viewer, Auth & Model Performance Diagnosis

## Root Cause 1: File Source 404 — Wrong path lookup

**Location**: [`main.py:594-611`](file:///d:/Intelligent_Static_Bug_Prediction/backend/app/main.py#L594-L611)

The `/api/v1/files/{file_id}/source` endpoint reads `db_file.path` directly with `os.path.exists(db_file.path)`. But `db_file.path` stores a **relative path** (e.g. `real_bugs_sample.py`) as set during upload at line 380 via `os.path.relpath(file_path, start=storage_path)`. The endpoint never reconstructs the absolute path by prepending the storage directory. Result: `os.path.exists("real_bugs_sample.py")` → `False` → 404 "File not found on disk".

Additionally, the endpoint returns `{"source": content}` but the File model stores `source_code` in the database already. The endpoint should return the DB-stored source (no disk dependency) along with file metadata, not just a raw `source` key.

**Fix**: Return `source_code` from the database (already loaded at upload time), and include `id`, `path`, `language`, `line_count`, `status` in the response. Remove the disk-read fallback (the DB is the source of truth). Remove the **duplicate** second endpoint — there is only one, but it has the wrong implementation.

## Root Cause 2: Annotations "No functions detected" — Wrong file path in parser

**Location**: [`main.py:627-644`](file:///d:/Intelligent_Static_Bug_Prediction/backend/app/main.py#L627-L644)

The `/api/v1/files/{file_id}/annotations` endpoint calls `parse_file(db_file.path)` with the **relative** path again. `os.path.exists(db_file.path)` returns `False` on disk, so the `if os.path.exists(...)` guard skips the entire parse → empty `functions` list → "No functions detected".

Even when fixed to use the absolute storage path, Windows backslash paths (`D:\...\real_bugs_sample.py`) may mismatch the parser's expectation. Need `os.path.normcase` + pathlib normalization.

**Fix**: Reconstruct absolute path from `STORAGE_DIR + projects/{project.id} + db_file.path`. Normalize with `pathlib.Path`. Also use Prediction start/end lines stored in DB rather than re-parsing.

## Root Cause 3: prediction_report same path bug

**Location**: [`main.py:674-695`](file:///d:/Intelligent_Static_Bug_Prediction/backend/app/main.py#L674-L695)

Same relative-path bug: `os.path.exists(pred.file.path)` → `False` → hotspots not loaded.

## Root Cause 4: Auth — 401 interceptor redirect loop

**Location**: [`api.ts:128-140`](file:///d:/Intelligent_Static_Bug_Prediction/frontend/src/lib/api.ts#L128-L140)

The 401 interceptor does `window.location.href = '/login'` which causes a hard navigation. If the user is already on `/login` and any API call returns 401 (e.g. a stale token check), it loops. The Layout component at line 13-17 only checks `localStorage.getItem('token')` existence — **any string** passes, including expired tokens.

**Fix**: 
- Interceptor should NOT redirect if already on `/login`.
- Layout should validate token by calling `GET /users/me` at startup.
- Add a `/auth/refresh` endpoint.
- Set `ACCESS_TOKEN_EXPIRE_MINUTES` to 480 (8 hours), configurable via env.

## Root Cause 5: SECRET_KEY defaults to "supersecretkey" in dev

**Location**: [`main.py:59-63`](file:///d:/Intelligent_Static_Bug_Prediction/backend/app/main.py#L59-L63)

The fallback is only allowed in development, but the warning is silent. Outside dev, it correctly raises. This is acceptable for dev but should log a warning.

## Root Cause 6: bcrypt compatibility

**Location**: [`requirements.txt`](file:///d:/Intelligent_Static_Bug_Prediction/backend/requirements.txt)

`passlib[bcrypt]` without pinning bcrypt version can cause `AttributeError` on newer bcrypt versions that removed `__about__`. Pin `bcrypt>=4.0.0,<5.0.0` and `passlib>=1.7.4`.

## Root Cause 7: Model Performance page — should be removed

The page exists at `/models/performance` with nav links in Layout sidebar and top bar. Per requirements, the page, route, nav links, and unused components should be removed. Keep the backend `/models/current` endpoint only for the model version display in BugDetailView.

## Root Cause 8: Frontend file_source field mismatch

The frontend at `ProjectViewer.tsx:69` reads `res.data.source` from the endpoint. The backend returns `{"source": content}`. After the fix, it should return `{"source_code": ...}` or `{"source": ...}` — we need consistency. We'll keep `source` as the field name in the response for the code viewer.

## Root Cause 9: Explorer shows flat list, not file tree

`ProjectViewer.tsx:199-231` maps `files` as a flat list with just the filename. No folder grouping from path segments.

## Root Cause 10: Missing file summary header

No language/line count/function count/risk summary shown above the code.

## Root Cause 11: No URL-based file selection

`ProjectViewer` only uses `useParams` for `projectId`. The selected file is only in React state. Refresh loses file selection.

## Summary of Fixes

| # | Bug | Root Cause | Fix |
|---|-----|-----------|-----|
| 1 | 404 on file source | Relative path not resolved to absolute | Return `source_code` from DB |
| 2 | No functions detected | `parse_file()` called with relative path | Use DB-stored prediction lines |
| 3 | prediction_report empty | Same relative path bug | Reconstruct absolute path |
| 4 | Auth redirect loop | 401 interceptor always redirects | Skip redirect on /login |
| 5 | Token too short | 30-min lifetime, no refresh | 8-hour default + refresh endpoint |
| 6 | bcrypt compat | Unpinned versions | Pin bcrypt>=4.0.0 |
| 7 | Model Performance page | Should be removed | Delete page, route, nav links |
| 8 | No file tree | Flat file list | Build tree from path segments |
| 9 | No file summary | Missing component | Add summary header |
| 10 | No URL file ID | State-only selection | Add `:fileId` to route |
| 11 | Ownership 403 vs 404 | Source returns 403 not 404 | Return 404 for not-found, 403 for not-owned |
