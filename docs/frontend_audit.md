# Frontend Audit

## 1. Pages & Components Classification

| Feature / Screen | File | What it calls | Backend Endpoint Needed | Exists? | Works? | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| Routing & Entry | `App.jsx`, `main.jsx` | None | None | N/A | Yes | **CORE** |
| Navigation Layout | `Layout.jsx` | None (Local storage token check) | None | N/A | Yes | **CORE** |
| Login / Register | `Login.jsx` | `POST /api/v1/auth/login`, `POST /api/v1/auth/register` | `/api/v1/auth/login`, `/api/v1/auth/register` | Yes | Yes | **CORE** |
| Project Dashboard | `Dashboard.jsx` | `GET /api/v1/projects`, `POST /api/v1/projects` (upload), `POST /api/v1/projects/{projectId}/analyze` | `/api/v1/projects`, `/api/v1/projects/{projectId}/analyze` | Yes | Yes | **CORE** |
| Risk Results Table | `AnalysisView.jsx` | `GET /api/v1/analysis/{runId}/status`, `GET /api/v1/analysis/{runId}/predictions` | `/api/v1/analysis/{runId}/status`, `/api/v1/analysis/{runId}/predictions` | Yes | Yes | **CORE** |
| Project Code Viewer | `ProjectViewer.jsx` | `GET /api/v1/projects/{projectId}/files`, `GET /api/v1/files/{fileId}/source`, `GET /api/v1/files/{fileId}/annotations` | `/api/v1/projects/{projectId}/files`, `/api/v1/files/{fileId}/source`, `/api/v1/files/{fileId}/annotations` | Yes | Yes | **CORE** |
| Explanation Page | `BugDetailView.jsx` | `GET /api/v1/predictions/{id}/report`, `POST /api/v1/predictions/{id}/feedback` | `/api/v1/predictions/{id}/report`, `/api/v1/predictions/{id}/feedback` | Yes | Yes | **CORE** |
| Run File Viewer | `FileViewer.jsx` | `GET /api/v1/analysis/{runId}/files`, `GET /api/v1/files/{fileId}/source`, `GET /api/v1/files/{fileId}/annotations` | (Same as ProjectViewer mostly) | Yes | Yes | **UNNECESSARY** (Duplicate of ProjectViewer) |

## 2. Hard-Coded & Mock Data Identified
- `Layout.jsx`: Contains hardcoded UI buttons for "Models", "Trends", "Demo workspace" with placeholder logic. Needs cleanup.
- `Dashboard.jsx`: Hardcoded "Demo" badge if project name contains "test".
- `BugDetailView.jsx`: Hardcoded `JSON.parse(report.explanation_json || "[]")` instead of properly typing.

## 3. Plan for Phase 2 (Cleanup)
- Remove `FileViewer.jsx` and route directly to `ProjectViewer.jsx` (which needs a route update to handle a selected file if needed).
- Remove hard-coded mock/placeholder buttons in `Layout.jsx` ("Trends", "Models") unless they can be wired.
- Create `src/lib/api.js` to centralize all Axios calls instead of having raw `axios.get/post` in every component.
- Consolidate types (or JSDoc if pure JS).
