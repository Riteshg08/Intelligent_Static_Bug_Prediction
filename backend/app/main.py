from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
import shutil
from fastapi import UploadFile, File as FastAPIFile, Form
from .worker import task_queue, run_analysis

from . import models, database

app = FastAPI(title="Intelligent Static Bug Prediction API")

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
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    return db.query(models.Project).filter(models.Project.owner_id == current_user.id).all()

@app.post("/api/v1/projects")
async def create_project(name: str = Form(...), file: UploadFile = FastAPIFile(...), current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    project = models.Project(name=name, owner_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    
    storage_path = f"../storage/projects/{project.id}"
    os.makedirs(storage_path, exist_ok=True)
    
    file_location = os.path.join(storage_path, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # extract zip if needed
    if file.filename.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(file_location, 'r') as zip_ref:
            zip_ref.extractall(storage_path)
            
    return {"id": project.id, "name": project.name}

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
    
    task_queue.enqueue(run_analysis, run.id)
    
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
    return preds
    
@app.get("/api/v1/predictions/{id}/report")
def prediction_report(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    pred = db.query(models.Prediction).join(models.File).join(models.Project).filter(
        models.Prediction.id == id,
        models.Project.owner_id == current_user.id
    ).first()
    if not pred:
        raise HTTPException(status_code=404)
    return pred
    
@app.post("/api/v1/predictions/{id}/feedback")
def submit_feedback(id: int, is_real_bug: bool, current_user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    feedback = models.Feedback(prediction_id=id, user_id=current_user.id, is_real_bug=is_real_bug)
    db.add(feedback)
    db.commit()
    return {"status": "saved"}

@app.get("/api/v1/models/current")
def get_current_model(current_user: models.User = Depends(get_current_user)):
    # in a real scenario we'd read the active.txt from models dir
    active_path = "../models/active.txt"
    if os.path.exists(active_path):
        with open(active_path, "r") as f:
            version = f.read().strip()
        return {"version": version}
    return {"version": "unknown"}

@app.get("/api/v1/languages")
def get_languages():
    return {"languages": ["Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Go"]}