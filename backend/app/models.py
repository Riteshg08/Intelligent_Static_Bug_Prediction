from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    projects = relationship("Project", back_populates="owner")
    feedbacks = relationship("Feedback", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    owner = relationship("User", back_populates="projects")
    files = relationship("File", back_populates="project")
    runs = relationship("AnalysisRun", back_populates="project")
    bug_reports = relationship("BugReport", back_populates="project")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    path = Column(String)
    language = Column(String, index=True)
    source_code = Column(String)
    line_count = Column(Integer)
    status = Column(String, default="pending")
    
    project = relationship("Project", back_populates="files")
    features = relationship("ExtractedFeature", back_populates="file")
    predictions = relationship("Prediction", back_populates="file")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="runs")
    predictions = relationship("Prediction", back_populates="run")

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    predictions = relationship("Prediction", back_populates="model_version")

class ExtractedFeature(Base):
    __tablename__ = "extracted_features"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    function_name = Column(String)
    language = Column(String)
    # Storing features as JSON string for simplicity, or we could have columns
    features_json = Column(String)
    
    file = relationship("File", back_populates="features")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), index=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    
    function_name = Column(String)
    language = Column(String, index=True)
    risk_score = Column(Float)
    risk_level = Column(String)
    confidence_note = Column(String)
    explanation_json = Column(String)
    
    file = relationship("File", back_populates="predictions")
    run = relationship("AnalysisRun", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
    feedback = relationship("Feedback", back_populates="prediction", uselist=False)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_real_bug = Column(Boolean)
    
    prediction = relationship("Prediction", back_populates="feedback")
    user = relationship("User", back_populates="feedbacks")

class BugReport(Base):
    __tablename__ = "bug_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    report_text = Column(String)
    
    project = relationship("Project", back_populates="bug_reports")

class Hotspot(Base):
    __tablename__ = "hotspots"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), index=True)
    file_id = Column(Integer, ForeignKey("files.id"), index=True)
    
    start_line = Column(Integer)
    end_line = Column(Integer)
    severity = Column(String)  # info | warning | high
    rule_id = Column(String)
    message = Column(String)
    
    run = relationship("AnalysisRun")
    file = relationship("File")
