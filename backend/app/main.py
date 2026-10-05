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

from . import models, database

app = FastAPI(title="Intelligent Static Bug Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

# Security config
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(database.get_db)):
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
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

@app.get("/api/v1/projects")
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
        func_count = 0
        last_updated = latest_run.created_at.isoformat() + "Z" if latest_run else None
        
        if latest_run and latest_run.status == "analyzed":
            preds = db.query(models.Prediction).filter(models.Prediction.run_id == latest_run.id).all()
            func_count = len(preds)
            for p in preds:
                if p.risk_level == "High": high += 1
                elif p.risk_level == "Medium": medium += 1
                else: low += 1
                
        result.append({
            "id": proj.id,
            "name": proj.name,
            "languages": langs,
            "risk_counts": {"high": high, "medium": medium, "low": low},
            "function_count": func_count,
            "last_updated": last_updated,
            "latest_run_id": latest_run.id if latest_run else None
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

@app.post("/api/v1/projects")
async def create_project(name: str = Form(...), file: UploadFile = FastAPIFile(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    project = models.Project(name=name, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    
    import tempfile
    
    # Store in project-scoped directory
    storage_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../storage"))
    storage_path = os.path.join(storage_base, f"projects/{project.id}")
    os.makedirs(storage_path, exist_ok=True)
    
    file_location = os.path.join(storage_path, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # extract zip if needed
    if file.filename.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(file_location, 'r') as zip_ref:
            zip_ref.extractall(storage_path)
            
    # Remove the zip file itself if it was extracted
    if file.filename.endswith(".zip"):
        os.remove(file_location)

    # Register files right away
    extensions_to_lang = {
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".py": "Python",
        ".go": "Go",
        ".java": "Java"
    }
    
    for root, _, files in os.walk(storage_path):
        for f in files:
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
                    line_count = len(content.splitlines())
            except UnicodeDecodeError:
                # Binary or unsupported encoding
                status = "unsupported"
                content = ""
                line_count = 0
                
            db_file = models.File(
                project_id=project.id,
                path=rel_path,
                language=lang,
                source_code=content,
                line_count=line_count,
                status=status
            )
            db.add(db_file)
    
    db.commit()

    return {"id": project.id, "name": project.name}

@app.get("/api/v1/projects/{project_id}/files")
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

@app.get("/api/v1/files/{file_id}/source")
def get_file_source(file_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    f = db.query(models.File).join(models.Project).filter(models.File.id == file_id, models.Project.owner_id == current_user.id).first()
    if not f:
        raise HTTPException(status_code=404)
        
    return {"source": f.source_code}

@app.delete("/api/v1/projects/{project_id}")
def delete_project(project_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id, models.Project.owner_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404)
    db.delete(project)
    db.commit()
    return {"status": "deleted"}

@app.post("/api/v1/projects/{project_id}/analyze")
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
        print(f"Warning: Redis not available ({e}), running analysis synchronously")
        run_analysis(run.id)
        
    return {"run_id": run.id, "status": "queued"}

@app.get("/api/v1/analysis/{run_id}/status")
def analysis_status(run_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    run = db.query(models.AnalysisRun).join(models.Project).filter(
        models.AnalysisRun.id == run_id, 
        models.Project.owner_id == current_user.id
    ).first()
    if not run:
        raise HTTPException(status_code=404)
    return {"status": run.status}

@app.get("/api/v1/analysis/{run_id}/predictions")
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
        "file_path": p.file.path if p.file else ""
    } for p in preds]
    
@app.get("/api/v1/analysis/{run_id}/files")
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
                "risk_counts": {"high": 0, "medium": 0, "low": 0}
            }
        f_data = files_map[p.file_id]
        if p.risk_score > f_data["max_risk_score"]:
            f_data["max_risk_score"] = p.risk_score
        if p.risk_level in f_data["risk_counts"]:
            f_data["risk_counts"][p.risk_level] += 1
            
    # Include files with hotspots but no predictions (e.g. only info/warning)
    hotspots = db.query(models.Hotspot).filter(models.Hotspot.run_id == run_id).all()
    for h in hotspots:
        if h.file_id not in files_map:
            files_map[h.file_id] = {
                "id": h.file_id,
                "path": h.file.path,
                "language": h.file.language,
                "max_risk_score": 0.0,
                "risk_counts": {"high": 0, "medium": 0, "low": 0}
            }
            
    return list(files_map.values())

@app.get("/api/v1/files/{file_id}/source")
def file_source(file_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    db_file = db.query(models.File).join(models.Project).filter(
        models.File.id == file_id,
        models.Project.owner_id == current_user.id
    ).first()
    if not db_file:
        raise HTTPException(status_code=403)
        
    try:
        if os.path.exists(db_file.path):
            with open(db_file.path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(1024 * 1024) # limit to 1MB
            return {"source": content}
        else:
            raise HTTPException(status_code=404, detail="File not found on disk")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/files/{file_id}/annotations")
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
    
    from sbp_analysis.parser import parse_file
    functions = []
    if os.path.exists(db_file.path):
        try:
            funcs = parse_file(db_file.path)
            for p in preds:
                func_info = next((f for f in funcs if f.function_name == p.function_name), None)
                if func_info:
                    functions.append({
                        "id": p.id,
                        "name": p.function_name,
                        "start_line": func_info.start_line,
                        "end_line": func_info.end_line,
                        "risk_score": p.risk_score,
                        "risk_level": p.risk_level
                    })
        except Exception:
            pass
            
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

@app.get("/api/v1/predictions/{id}/report")
def prediction_report(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    pred = db.query(models.Prediction).join(models.File).join(models.Project).filter(
        models.Prediction.id == id,
        models.Project.owner_id == current_user.id
    ).first()
    if not pred:
        raise HTTPException(status_code=404)
        
    import json
    from sbp_analysis.parser import parse_file
    
    hotspots_list = []
    try:
        if os.path.exists(pred.file.path):
            funcs = parse_file(pred.file.path)
            func_info = next((f for f in funcs if f.function_name == pred.function_name), None)
            
            if func_info:
                hotspots = db.query(models.Hotspot).filter(
                    models.Hotspot.file_id == pred.file_id,
                    models.Hotspot.run_id == pred.run_id,
                    models.Hotspot.start_line >= func_info.start_line,
                    models.Hotspot.end_line <= func_info.end_line
                ).all()
                hotspots_list = [{
                    "severity": h.severity,
                    "rule_id": h.rule_id,
                    "message": h.message,
                    "start_line": h.start_line,
                    "end_line": h.end_line
                } for h in hotspots]
    except Exception:
        pass
        
    return {
        "id": pred.id,
        "function_name": pred.function_name,
        "language": pred.language,
        "risk_score": pred.risk_score,
        "risk_level": pred.risk_level,
        "confidence_note": pred.confidence_note,
        "explanation": json.loads(pred.explanation_json) if pred.explanation_json else {},
        "hotspots": hotspots_list,
        "file_id": pred.file_id
    }
    
@app.post("/api/v1/predictions/{id}/feedback")
def submit_feedback(id: int, is_real_bug: bool, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    feedback = models.Feedback(prediction_id=id, user_id=current_user.id, is_real_bug=is_real_bug)
    db.add(feedback)
    db.commit()
    return {"status": "saved"}

@app.get("/api/v1/models/current")
def get_current_model(current_user: models.User = Depends(get_current_user)):
    active_path = "../models/active.txt"
    if os.path.exists(active_path):
        with open(active_path, "r") as f:
            version = f.read().strip()
        return {"version": version}
    return {"version": "unknown"}

@app.get("/api/v1/languages")
def get_languages():
    return {"languages": ["Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go"]}