from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
import shutil
from fastapi import UploadFile, File as FastAPIFile, Form
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static-analysis')))

from .worker import task_queue, run_analysis

from typing import List
from . import models, database, schemas
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create tables
models.Base.metadata.create_all(bind=database.engine)
from fastapi import Request
import json
from pythonjsonlogger import jsonlogger
import logging

# Structured JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Intelligent Static Bug Prediction API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
origins = [url.strip() for url in frontend_url.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# removed create_all so Alembic is the single source of truth

# Security config
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("ENV", "development") != "development":
        raise ValueError("SECRET_KEY must be set outside development environment.")
    SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/v1/auth/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_token(request: Request, current_user: models.User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": current_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
def health_check():
    health_status = {"status": "ok", "db": "ok", "redis": "ok", "model": "ok"}
    try:
        db = database.SessionLocal()
        db.execute(database.text("SELECT 1"))
        db.close()
    except Exception as e:
        health_status["db"] = f"error: {str(e)}"
        health_status["status"] = "error"
        
    try:
        from .worker import redis_conn
        redis_conn.ping()
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
        health_status["status"] = "error"
        
    try:
        active_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/active.txt"))
        if not os.path.exists(active_path):
            active_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/active.txt"))
        if not os.path.exists(active_path):
            health_status["model"] = "not loaded"
    except Exception as e:
        health_status["model"] = f"error: {str(e)}"
        health_status["status"] = "error"
        
    if health_status["status"] != "ok":
        raise HTTPException(status_code=503, detail=health_status)
    return health_status

@app.post("/api/v1/auth/register", response_model=Token)
@limiter.limit("5/minute")
def register(request: Request, user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}

@app.get("/api/v1/projects", response_model=List[schemas.ProjectResponse])
def get_projects(current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    projects = db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()
    result = []
    for proj in projects:
        # Get languages from files
        langs = list(set([f.language for f in proj.files if f.language and f.language != "Unknown"]))
        
        # Get latest run
        latest_run = db.query(models.AnalysisRun).filter(models.AnalysisRun.project_id == proj.id).order_by(models.AnalysisRun.created_at.desc()).first()
        
        high = 0
        medium = 0
        low = 0
        p_high = 0
        p_medium = 0
        p_low = 0
        func_count = 0
        last_updated = latest_run.created_at.isoformat() + "Z" if latest_run else None
        status = latest_run.status if latest_run else "unknown"
        
        if latest_run and latest_run.status in ["analyzed", "completed"]:
            preds = db.query(models.Prediction).filter(models.Prediction.run_id == latest_run.id).all()
            func_count = len(preds)
            for p in preds:
                if p.risk_level == "High": high += 1
                elif p.risk_level == "Medium": medium += 1
                else: low += 1
                
                if p.pattern_severity and 'high' in p.pattern_severity:
                    p_high += 1
                elif p.pattern_severity and 'warning' in p.pattern_severity:
                    p_medium += 1
                elif p.pattern_severity and 'info' in p.pattern_severity:
                    p_low += 1
                
        result.append({
            "id": proj.id,
            "name": proj.name,
            "languages": langs,
            "risk_counts": {"high": high, "medium": medium, "low": low},
            "pattern_counts": {"high": p_high, "medium": p_medium, "low": p_low},
            "function_count": func_count,
            "last_updated": last_updated,
            "latest_run_id": latest_run.id if latest_run else None,
            "status": status
        })
    return result

@app.delete("/api/v1/projects/{project_id}")
def delete_project(project_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # cascade delete manually
    runs = db.query(models.AnalysisRun).filter(models.AnalysisRun.project_id == project_id).all()
    run_ids = [run.id for run in runs]
    
    files = db.query(models.File).filter(models.File.project_id == project_id).all()
    file_ids = [f.id for f in files]
    
    if run_ids:
        db.query(models.Hotspot).filter(models.Hotspot.run_id.in_(run_ids)).delete(synchronize_session=False)
        preds = db.query(models.Prediction).filter(models.Prediction.run_id.in_(run_ids)).all()
        pred_ids = [p.id for p in preds]
        if pred_ids:
            db.query(models.Feedback).filter(models.Feedback.prediction_id.in_(pred_ids)).delete(synchronize_session=False)
        db.query(models.Prediction).filter(models.Prediction.run_id.in_(run_ids)).delete(synchronize_session=False)
        db.query(models.AnalysisRun).filter(models.AnalysisRun.id.in_(run_ids)).delete(synchronize_session=False)
        
    if file_ids:
        db.query(models.ExtractedFeature).filter(models.ExtractedFeature.file_id.in_(file_ids)).delete(synchronize_session=False)
        preds = db.query(models.Prediction).filter(models.Prediction.file_id.in_(file_ids)).all()
        pred_ids = [p.id for p in preds]
        if pred_ids:
            db.query(models.Feedback).filter(models.Feedback.prediction_id.in_(pred_ids)).delete(synchronize_session=False)
            db.query(models.Prediction).filter(models.Prediction.file_id.in_(file_ids)).delete(synchronize_session=False)
        db.query(models.File).filter(models.File.id.in_(file_ids)).delete(synchronize_session=False)
        
    db.query(models.BugReport).filter(models.BugReport.project_id == project_id).delete(synchronize_session=False)
    db.delete(project)
    db.commit()
    
    # Delete from storage
    storage_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../storage"))
    storage_path = os.path.join(storage_base, f"projects/{project_id}")
    if os.path.exists(storage_path):
        import shutil
        shutil.rmtree(storage_path)
        
    return {"status": "success"}

import tempfile
import zipfile
import tarfile
from threading import Thread
import logging

logger = logging.getLogger(__name__)

default_storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../storage"))
STORAGE_DIR = os.path.abspath(os.getenv("STORAGE_DIR", default_storage_dir))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 50 * 1024 * 1024)) # 50MB
MAX_EXTRACTED_SIZE = int(os.getenv("MAX_EXTRACTED_SIZE", 200 * 1024 * 1024)) # 200MB
MAX_FILES_COUNT = int(os.getenv("MAX_FILES_COUNT", 10000))
ALLOWED_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".c", ".h", ".cpp", ".hpp", ".cc", ".cs", ".zip", ".tar.gz"}
IGNORED_DIRS = {"node_modules", "vendor", "dist", "build", ".git"}
MAX_COMPRESSION_RATIO = 100

def is_safe_path(base_path, target_path, is_symlink=False):
    if is_symlink:
        return False
    if os.path.isabs(target_path):
        return False
    resolved_target = os.path.abspath(os.path.join(base_path, target_path))
    return resolved_target.startswith(os.path.abspath(base_path))

@app.post("/api/v1/projects", response_model=schemas.ProjectCreateResponse)
@limiter.limit("5/minute")
async def create_project(request: Request, name: str = Form(...), file: UploadFile = FastAPIFile(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    # Check extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS and not (file.filename.endswith(".tar.gz") and ".tar.gz" in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed.")
        
    project = models.Project(name=name, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    
    storage_path = os.path.join(STORAGE_DIR, f"projects/{project.id}")
    os.makedirs(storage_path, exist_ok=True)
    
    file_location = os.path.join(storage_path, file.filename)
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:
        db.delete(project)
        db.commit()
        raise HTTPException(status_code=413, detail="Uploaded file is too large.")
        
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    extracted_size = 0
    extracted_files = 0
    
    try:
        if file.filename.endswith(".zip"):
            with zipfile.ZipFile(file_location, 'r') as zip_ref:
                for zinfo in zip_ref.infolist():
                    if zinfo.file_size > 0 and zinfo.compress_size > 0:
                        ratio = zinfo.file_size / zinfo.compress_size
                        if ratio > MAX_COMPRESSION_RATIO:
                            raise HTTPException(status_code=400, detail="Zip bomb detected (high compression ratio).")
                    if not is_safe_path(storage_path, zinfo.filename):
                        raise HTTPException(status_code=400, detail="Zip slip vulnerability detected.")
                    extracted_size += zinfo.file_size
                    extracted_files += 1
                    if extracted_size > MAX_EXTRACTED_SIZE or extracted_files > MAX_FILES_COUNT:
                        raise HTTPException(status_code=413, detail="Extracted archive too large or too many files.")
                zip_ref.extractall(storage_path)
            os.remove(file_location)
        elif file.filename.endswith(".tar.gz"):
            with tarfile.open(file_location, 'r:gz') as tar_ref:
                for member in tar_ref.getmembers():
                    if member.islnk() or member.issym():
                        raise HTTPException(status_code=400, detail="Symlinks not allowed in archive.")
                    if not is_safe_path(storage_path, member.name):
                        raise HTTPException(status_code=400, detail="Tar slip vulnerability detected.")
                    extracted_size += member.size
                    extracted_files += 1
                    if extracted_size > MAX_EXTRACTED_SIZE or extracted_files > MAX_FILES_COUNT:
                        raise HTTPException(status_code=413, detail="Extracted archive too large or too many files.")
                tar_ref.extractall(storage_path)
            os.remove(file_location)
    except HTTPException:
        db.delete(project)
        db.commit()
        shutil.rmtree(storage_path)
        raise
    except Exception as e:
        db.delete(project)
        db.commit()
        shutil.rmtree(storage_path)
        raise HTTPException(status_code=400, detail=f"Failed to process archive: {str(e)}")

    extensions_to_lang = {
        ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
        ".py": "Python", ".go": "Go", ".java": "Java", ".c": "C", ".h": "C", 
        ".cpp": "C++", ".hpp": "C++", ".cc": "C++", ".cs": "C#"
    }
    
    # Bulk insert files for speed
    files_to_insert = []
    
    for root, dirs, files in os.walk(storage_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for f in files:
            if f.endswith(".min.js") or f.endswith(".min.css"):
                continue
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, start=storage_path)
            
            ext = os.path.splitext(f)[1].lower()
            if ext in extensions_to_lang:
                lang = extensions_to_lang[ext]
                status = "pending"
            else:
                lang = "Unknown"
                status = "unsupported"
                
            try:
                with open(file_path, "r", encoding="utf-8") as source_file:
                    content = source_file.read()
                    if "\x00" in content: # binary file check
                        status = "unsupported"
                        content = ""
                    line_count = len(content.splitlines())
            except UnicodeDecodeError:
                status = "unsupported"
                content = ""
                line_count = 0
                
            files_to_insert.append(models.File(
                project_id=project.id,
                path=rel_path,
                language=lang,
                source_code=content,
                line_count=line_count,
                status=status
            ))
            
    db.bulk_save_objects(files_to_insert)
    db.commit()

    return {"id": project.id, "name": project.name}

@app.get("/api/v1/projects/{project_id}/files", response_model=schemas.ProjectFilesResponse)
def get_project_files(project_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404)
        
    files = db.query(models.File).filter(models.File.project_id == project.id).all()
    result = []
    
    latest_run = db.query(models.AnalysisRun).filter(models.AnalysisRun.project_id == project.id).order_by(models.AnalysisRun.created_at.desc()).first()
    
    for f in files:
        risk_level = "Unknown"
        if latest_run and f.status == "analyzed":
            preds = db.query(models.Prediction).filter(models.Prediction.file_id == f.id, models.Prediction.run_id == latest_run.id).all()
            if any(p.risk_level == "High" for p in preds):
                risk_level = "High"
            elif any(p.risk_level == "Medium" for p in preds):
                risk_level = "Medium"
            elif preds:
                risk_level = "Low"
        
        result.append({
            "id": f.id,
            "path": f.path,
            "language": f.language,
            "line_count": f.line_count,
            "status": f.status,
            "risk_level": risk_level
        })
        
    return {
        "run_id": latest_run.id if latest_run else None,
        "run_status": latest_run.status if latest_run else None,
        "files": result
    }




@app.post("/api/v1/projects/{project_id}/analyze", response_model=schemas.AnalysisRunResponse)
def analyze_project(project_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404)
        
    run = models.AnalysisRun(project_id=project.id, status="queued")
    db.add(run)
    db.commit()
    db.refresh(run)
    
    try:
        task_queue.enqueue(run_analysis, run.id)
    except Exception as e:
        logger.warning(f"Redis not available ({e}), running analysis in background thread")
        Thread(target=run_analysis, args=(run.id,)).start()
        
    return {"run_id": run.id, "status": "queued"}

@app.get("/api/v1/analysis/{run_id}/status", response_model=schemas.StatusResponse)
def analysis_status(run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    run = db.query(models.AnalysisRun).join(models.Project).filter(
        models.AnalysisRun.id == run_id, 
        models.Project.owner_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=404)
    
    import json
    skipped_reasons = {}
    if run.skipped_reasons:
        try:
            skipped_reasons = json.loads(run.skipped_reasons)
        except:
            pass
            
    return {
        "status": run.status,
        "files_total": run.files_total,
        "files_done": run.files_done,
        "files_skipped": run.files_skipped,
        "skipped_reasons": skipped_reasons,
        "functions_found": run.functions_found,
        "error_message": run.error_message
    }

@app.get("/api/v1/analysis/{run_id}/predictions", response_model=List[schemas.PredictionResponse])
def analysis_predictions(run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    run = db.query(models.AnalysisRun).join(models.Project).filter(
        models.AnalysisRun.id == run_id, 
        models.Project.owner_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=404)
        
    preds = db.query(models.Prediction).filter(models.Prediction.run_id == run_id).all()
    return [{
        "id": p.id,
        "function_name": p.function_name,
        "language": p.language,
        "start_line": p.start_line,
        "end_line": p.end_line,
        "risk_score": p.risk_score,
        "risk_level": p.risk_level,
        "file_id": p.file_id,
        "file_path": p.file.path if p.file else "",
        "pattern_severity": p.pattern_severity or "none"
    } for p in preds]
    
@app.get("/api/v1/analysis/{run_id}/files", response_model=List[schemas.AnalysisFileResponse])
def analysis_files(run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    run = db.query(models.AnalysisRun).join(models.Project).filter(
        models.AnalysisRun.id == run_id, 
        models.Project.owner_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=404)
        
    predictions = db.query(models.Prediction).filter(models.Prediction.run_id == run_id).all()
    files_map = {}
    
    for p in predictions:
        if p.file_id not in files_map:
            files_map[p.file_id] = {
                "id": p.file_id,
                "path": p.file.path,
                "language": p.file.language,
                "max_risk_score": 0.0,
                "mean_risk_score": 0.0,
                "risk_scores_sum": 0.0,
                "function_count": 0,
                "hotspot_count": 0,
                "risk_counts": {"high": 0, "medium": 0, "low": 0}
            }
        f_data = files_map[p.file_id]
        if p.risk_score > f_data["max_risk_score"]:
            f_data["max_risk_score"] = p.risk_score
            
        if "function_lines_sum" not in f_data:
            f_data["function_lines_sum"] = 0
            
        length = 1
        if p.end_line and p.start_line:
            length = max(1, p.end_line - p.start_line + 1)
            
        f_data["risk_scores_sum"] += p.risk_score * length
        f_data["function_count"] += 1
        f_data["function_lines_sum"] += length
        
        if p.risk_level.lower() in f_data["risk_counts"]:
            f_data["risk_counts"][p.risk_level.lower()] += 1
        else:
            f_data["risk_counts"][p.risk_level] = f_data["risk_counts"].get(p.risk_level, 0) + 1
            
    # Include files with hotspots but no predictions (e.g. only info/warning)
    hotspots = db.query(models.Hotspot).filter(models.Hotspot.run_id == run_id).all()
    for h in hotspots:
        if h.file_id not in files_map:
            files_map[h.file_id] = {
                "id": h.file_id,
                "path": h.file.path,
                "language": h.file.language,
                "max_risk_score": 0.0,
                "mean_risk_score": 0.0,
                "risk_scores_sum": 0.0,
                "function_count": 0,
                "hotspot_count": 0,
                "risk_counts": {"high": 0, "medium": 0, "low": 0},
                "function_lines_sum": 0
            }
        files_map[h.file_id]["hotspot_count"] += 1
            
    for f_data in files_map.values():
        if f_data.get("function_lines_sum", 0) > 0:
            f_data["mean_risk_score"] = f_data["risk_scores_sum"] / f_data["function_lines_sum"]
            
    return list(files_map.values())

@app.get("/api/v1/files/{file_id}/source")
def file_source(file_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    project = db.query(models.Project).filter(models.Project.id == db_file.project_id).first()
    if not project or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
        
    return {
        "id": db_file.id,
        "path": db_file.path,
        "language": db_file.language,
        "line_count": db_file.line_count,
        "status": db_file.status,
        "source": db_file.source_code
    }

@app.get("/api/v1/files/{file_id}/annotations", response_model=schemas.AnnotationsResponse)
def file_annotations(file_id: int, run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    db_file = db.query(models.File).join(models.Project).filter(
        models.File.id == file_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=403)
        
    preds = db.query(models.Prediction).filter(
        models.Prediction.file_id == file_id,
        models.Prediction.run_id == run_id
    ).all()
    
    functions = []
    for p in preds:
        functions.append({
            "id": p.id,
            "name": p.function_name,
            "start_line": p.start_line,
            "end_line": p.end_line,
            "risk_score": p.risk_score,
            "risk_level": p.risk_level
        })
            
    hotspots = db.query(models.Hotspot).filter(
        models.Hotspot.file_id == file_id,
        models.Hotspot.run_id == run_id
    ).all()
    
    hotspots_list = [{
        "id": h.id,
        "start_line": h.start_line,
        "end_line": h.end_line,
        "severity": h.severity,
        "rule_id": h.rule_id,
        "message": h.message
    } for h in hotspots]
    
    return {"functions": functions, "hotspots": hotspots_list}

@app.get("/api/v1/predictions/{id}/report", response_model=schemas.PredictionReportResponse)
def prediction_report(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    pred = db.query(models.Prediction).join(models.File).join(models.Project).filter(
        models.Prediction.id == id,
        models.Project.owner_id == current_user.id
    ).first()
    if not pred:
        raise HTTPException(status_code=404)
        
    import json
    hotspots_list = []
    if pred.start_line is not None and pred.end_line is not None:
        hotspots = db.query(models.Hotspot).filter(
            models.Hotspot.file_id == pred.file_id,
            models.Hotspot.run_id == pred.run_id,
            models.Hotspot.start_line >= pred.start_line,
            models.Hotspot.end_line <= pred.end_line
        ).all()
        hotspots_list = [{
            "severity": h.severity,
            "rule_id": h.rule_id,
            "message": h.message,
            "start_line": h.start_line,
            "end_line": h.end_line
        } for h in hotspots]
        
    return {
        "id": pred.id,
        "function_name": pred.function_name,
        "language": pred.language,
        "risk_score": pred.risk_score,
        "risk_level": pred.risk_level,
        "confidence_note": pred.confidence_note,
        "explanation": json.loads(pred.explanation_json) if pred.explanation_json else {},
        "hotspots": hotspots_list,
        "file_id": pred.file_id,
        "pattern_severity": pred.pattern_severity or "none"
    }
    
@app.post("/api/v1/predictions/{id}/feedback", response_model=schemas.StatusResponse)
def submit_feedback(id: int, feedback_in: schemas.FeedbackRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    pred = db.query(models.Prediction).join(models.File).join(models.Project).filter(
        models.Prediction.id == id,
        models.Project.owner_id == current_user.id
    ).first()
    if not pred:
        raise HTTPException(status_code=403, detail="Prediction not found or not owned by user")
        
    feedback = db.query(models.Feedback).filter(
        models.Feedback.prediction_id == id,
        models.Feedback.user_id == current_user.id
    ).first()
    
    if feedback:
        feedback.is_real_bug = feedback_in.is_real_bug
        feedback.comment = feedback_in.comment
    else:
        feedback = models.Feedback(
            prediction_id=id, 
            user_id=current_user.id, 
            is_real_bug=feedback_in.is_real_bug,
            comment=feedback_in.comment
        )
        db.add(feedback)
    
    db.commit()
    return {"status": "saved"}

@app.get("/api/v1/predictions/{id}/feedback", response_model=schemas.FeedbackResponse)
def get_feedback(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    feedback = db.query(models.Feedback).filter(
        models.Feedback.prediction_id == id,
        models.Feedback.user_id == current_user.id
    ).first()
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
        
    return {
        "id": feedback.id,
        "prediction_id": feedback.prediction_id,
        "user_id": feedback.user_id,
        "is_real_bug": feedback.is_real_bug,
        "comment": feedback.comment,
        "created_at": feedback.created_at.isoformat() + "Z" if feedback.created_at else "",
        "updated_at": feedback.updated_at.isoformat() + "Z" if feedback.updated_at else ""
    }

@app.get("/api/v1/models/current")
def get_current_model(current_user: models.User = Depends(get_current_user)):
    # Read MODELS_DIR from env, fallback to ../models
    models_dir = os.environ.get("MODELS_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models")))
    active_path = os.path.join(models_dir, "active.txt")
    
    if os.path.exists(active_path):
        with open(active_path, "r") as f:
            version = f.read().strip()
            
        metadata_path = os.path.join(models_dir, version, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as mf:
                metadata = json.load(mf)
            return {
                "active_model": version,
                "metadata": metadata
            }
    
    raise HTTPException(status_code=404, detail="Model not trained")

@app.get("/api/v1/languages", response_model=schemas.LanguagesResponse)
def get_languages():
    return {"languages": ["Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go"]}

@app.get("/api/v1/analysis/{run_id}/export")
def export_analysis_json(run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    run = db.query(models.AnalysisRun).join(models.Project).filter(
        models.AnalysisRun.id == run_id, 
        models.Project.owner_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=404)
        
    preds = db.query(models.Prediction).filter(models.Prediction.run_id == run_id).all()
    results = []
    for p in preds:
        results.append({
            "function": p.function_name,
            "language": p.language,
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "file": p.file.path if p.file else ""
        })
    return {"project_id": run.project_id, "run_id": run_id, "findings": results}

@app.get("/api/v1/analysis/{run_id}/status/languages")
def analysis_status_by_language(run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    run = db.query(models.AnalysisRun).join(models.Project).filter(
        models.AnalysisRun.id == run_id, 
        models.Project.owner_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=404)
        
    files = db.query(models.File).filter(models.File.project_id == run.project_id).all()
    lang_status = {}
    for f in files:
        if f.language not in lang_status:
            lang_status[f.language] = {"total": 0, "analyzed": 0, "pending": 0, "failed": 0, "skipped": 0}
        lang_status[f.language]["total"] += 1
        st = f.status if f.status in ["analyzed", "pending", "failed", "skipped"] else "pending"
        lang_status[f.language][st] += 1
        
    return lang_status