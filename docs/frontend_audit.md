# Frontend Audit

## Pages / Components
- `App.jsx` -> FIX (Rename `Dashboard` route to `/projects`, add `404` and `ErrorBoundary`)
- `components/Layout.jsx` -> FIX (Remove Bell, Workspace dropdown, unused nav items, "Overview" duplicate. Make "New scan" open upload dialog. Fix breadcrumbs.)
- `pages/Login.jsx` -> FIX (Convert to TypeScript `Login.tsx`, add dark mode)
- `pages/Dashboard.jsx` -> FIX (Convert to `ProjectsView.tsx`, update route to `/projects`, add dark mode, use `api.ts`)
- `pages/ProjectViewer.jsx` -> FIX (Convert to `ProjectViewer.tsx`, add dark mode, use `api.ts`)
- `pages/AnalysisView.jsx` -> FIX (Convert to `AnalysisView.tsx`, add dark mode, fix Findings panel default filter, use `api.ts`)
- `pages/BugDetailView.jsx` -> FIX (Convert to `BugDetailView.tsx`, add dark mode, use `api.ts`)
- `pages/ModelPerformance.jsx` -> FIX (Convert to `ModelPerformance.tsx`, add dark mode, use `api.ts`)
- `lib/api.ts` -> KEEP / FIX (Ensure it has centralized error handling and toasts)

## Routes
- `/login` -> KEEP
- `/` -> REMOVE (Redirect to `/projects`)
- `/projects` -> KEEP (formerly `/`)
- `/projects/:projectId` -> KEEP
- `/analysis/:runId` -> KEEP
- `/prediction/:id` -> KEEP
- `/models/performance` -> KEEP
- `*` (404) -> KEEP (Add)

## Nav Items & Buttons
- Bell button -> REMOVE
- Workspace dropdown -> REMOVE
- "Overview" duplicate -> REMOVE
- "Code review" tab (no route) -> REMOVE
- "Results" tab (no route) -> REMOVE
- "New scan" button -> FIX (Make it open the upload dialog)
- "Sun/Moon" dark mode toggle -> FIX (Persist in localStorage, toggle class)

## General Tasks
- Convert everything to TypeScript `.tsx`.
- Centralize API calls in `api.ts`.
- Add `dark:` classes to all pages and components.
- Ensure build passes.
