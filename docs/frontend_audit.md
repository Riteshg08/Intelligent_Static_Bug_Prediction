# Frontend Audit

## Features & APIs

| feature/screen | API it calls | backend endpoint needed | exists in backend? | works? | Status |
|---|---|---|---|---|---|
| **Login / Register** (`Login.jsx`) | `POST /auth/login`<br>`POST /auth/register` | `POST /api/v1/auth/login`<br>`POST /api/v1/auth/register` | Yes | Yes | CORE |
| **Dashboard (List projects & risk scores)** (`Dashboard.jsx`) | `GET /projects` | `GET /api/v1/projects` | Yes | Yes | CORE |
| **Dashboard (Upload)** (`Dashboard.jsx`) | `POST /projects` | `POST /api/v1/projects` | Yes | Yes | CORE |
| **Dashboard (Analysis progress trigger)** (`Dashboard.jsx`) | `POST /projects/{id}/analyze` | `POST /api/v1/projects/{id}/analyze` | Yes | Yes | CORE |
| **Dashboard (Delete project)** (`Dashboard.jsx`) | `DELETE /projects/{id}` | `DELETE /api/v1/projects/{id}` | Yes | Yes | CORE |
| **Project Viewer (Files list)** (`ProjectViewer.jsx`) | `GET /projects/{id}/files` | `GET /api/v1/projects/{id}/files` | Yes | Yes | CORE |
| **Project Viewer (Source code viewer with line numbers)** (`ProjectViewer.jsx`) | `GET /files/{id}/source` | `GET /api/v1/files/{id}/source` | Yes | Yes | CORE |
| **Project Viewer (Function range tinting, Risky-line highlighting, Findings panel)** (`ProjectViewer.jsx`) | `GET /files/{id}/annotations?run_id={id}` | `GET /api/v1/files/{id}/annotations` | Yes | Yes | CORE |
| **Analysis View (Analysis progress status)** (`AnalysisView.jsx`) | `GET /analysis/{id}/status` | `GET /api/v1/analysis/{id}/status` | Yes | Yes | CORE |
| **Analysis View (Ranked results table, Risk score, Low/Medium/High badges)** (`AnalysisView.jsx`) | `GET /analysis/{id}/predictions` | `GET /api/v1/analysis/{id}/predictions` | Yes | Yes | CORE |
| **Bug Detail View (Explanation page)** (`BugDetailView.jsx`) | `GET /predictions/{id}/report` | `GET /api/v1/predictions/{id}/report` | Yes | Yes | CORE |
| **Bug Detail View (Feedback buttons)** (`BugDetailView.jsx`) | `POST /predictions/{id}/feedback?is_real_bug={bool}` | `POST /api/v1/predictions/{id}/feedback` | Yes | Yes | CORE |
| **File Viewer** (`FileViewer.jsx`) | None | None | N/A | N/A | UNNECESSARY |
| **App CSS** (`App.css`) | None | None | N/A | N/A | UNNECESSARY |
| **Template Assets** (`assets/hero.png`, `react.svg`, `vite.svg`) | None | None | N/A | N/A | UNNECESSARY |
| **Mock Tests / Files** (`__tests__/AnalysisView.test.jsx`, `App.test.jsx`) | None | None | N/A | N/A | UNNECESSARY |

## Summary of Removals & Additions
- All backend endpoints currently required by the frontend are present in the backend (`backend/app/main.py`) and appear functional. 
- The features explicitly requested to be **CORE** are fully covered by `Dashboard`, `ProjectViewer`, `AnalysisView`, `BugDetailView`, and `Login` pages. JSON export is available in `AnalysisView.jsx`.
- **UNNECESSARY** items to be removed: `FileViewer.jsx` (deprecated), `App.css` (unused styles), template assets (`hero.png`, `react.svg`, `vite.svg`), and unused mock/test files.
