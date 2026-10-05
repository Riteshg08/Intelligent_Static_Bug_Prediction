# Viewer & Auth Diagnosis

## 1. Code-view Chain and "No functions detected"
- **Upload**: Files are stored and registered correctly in the `files` table with the relative path. 
- **Duplicate Endpoint**: The prompt mentioned a duplicate `/api/v1/files/{file_id}/source` endpoint, but current analysis shows only one is present in `main.py` which already returns `{id, path, language, line_count, status, source}` correctly. The frontend reads `.source`. We will leave this working endpoint intact.
- **Ownership Check**: `main.py` correctly checks ownership via the `project_id` and `current_user.id` join, returning 404 for missing files and 403 for unauthorized access.
- **Frontend Explorer**: The explorer tree correctly maps paths to files and uses the numeric `fileId` when fetching the source.
- **"No functions detected" Issue**: The worker fails to map the analysis results back to the database files on Windows because `os.path.abspath(os.path.join(storage_path, f.path))` can mix backslashes and forward slashes, causing a mismatch with the `file_path` generated during extraction (which uses `os.path.join(root, file)`). We will fix this by using `pathlib.Path` in `worker.py` for consistent path normalization on Windows.

## 2. Authentication
- **Token Lifetime**: Currently hardcoded to 480 minutes (8 hours) in `main.py` rather than reading from env. We will update it to read `ACCESS_TOKEN_EXPIRE_MINUTES` from the environment or default to 480.
- **SECRET_KEY**: The default is `supersecretkey`. In non-dev environments, it correctly raises a `ValueError` if not set.
- **Bcrypt/Passlib**: We will pin `bcrypt==4.0.1` and `passlib==1.7.4` to avoid compatibility errors.
- **401 Loop**: The frontend interceptor in `api.ts` checks `if (window.location.pathname !== '/login')` before redirecting to `/login` after clearing the token, which prevents the loop. We will ensure this logic is robust.
- **Layout token check**: We need to ensure the route guard uses `/users/me` to validate the token rather than just checking its presence.

## 3. UI Fixes
- **Code Viewer**: Will fix the frontend to show source code escaped properly immediately after upload (before analysis finishes).
- **Explorer**: Will ensure the file tree is a proper tree.
- **Error States**: Will implement clear error messages for failed analyses.
- **Model Performance**: Will remove the model performance page and related UI.
