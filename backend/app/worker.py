import os
import zipfile
import tarfile
from redis import Redis
from rq import Worker, Queue
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
from sbp_analysis.cli import analyze_directory
from sbp_predict.engine import PredictionEngine
import re

redis_conn = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)
task_queue = Queue("analysis", connection=redis_conn)

engine = PredictionEngine(models_dir="../models")

def detect_secrets(file_path):
    secrets_found = False
    with open(file_path, 'r', errors='ignore') as f:
        content = f.read()
        if re.search(r'(?i)(password|secret|key|token)\s*=\s*[\'"][^\'"]+[\'"]', content):
            secrets_found = True
    return secrets_found

def run_analysis(run_id: int):
    db: Session = SessionLocal()
    try:
        run = db.query(models.AnalysisRun).filter(models.AnalysisRun.id == run_id).first()
        if not run:
            return
            
        run.status = "running"
        db.commit()
        
        project = db.query(models.Project).filter(models.Project.id == run.project_id).first()
        
        # Analyze project files
        storage_path = f"../storage/projects/{project.id}"
        
        # We can extract features
        df = analyze_directory(storage_path)
        features = df.to_dict('records')
        
        # Save files to db if not exists
        for feat in features:
            file_path = feat['file_path']
            lang = feat['language']
            
            db_file = db.query(models.File).filter(
                models.File.project_id == project.id,
                models.File.path == file_path
            ).first()
            
            if not db_file:
                db_file = models.File(project_id=project.id, path=file_path, language=lang)
                db.add(db_file)
                db.commit()
                db.refresh(db_file)
                
            # predict
            pred_results = engine.predict([feat])
            if pred_results:
                p = pred_results[0]
                
                # Check for secrets
                if detect_secrets(file_path):
                    p['confidence_note'] = (p.get('confidence_note', '') + " | SECRET DETECTED").strip()
                    
                prediction = models.Prediction(
                    file_id=db_file.id,
                    run_id=run.id,
                    function_name=p['function_name'],
                    language=p['language'],
                    risk_score=p['risk_score'],
                    risk_level=p['risk_level'],
                    confidence_note=p['confidence_note'],
                    explanation_json=str(p['explanation'])
                )
                db.add(prediction)
        
        run.status = "completed"
        db.commit()
    except Exception as e:
        run = db.query(models.AnalysisRun).filter(models.AnalysisRun.id == run_id).first()
        if run:
            run.status = "failed"
            db.commit()
        print(f"Error in analysis: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    worker = Worker([task_queue], connection=redis_conn)
    worker.work()
