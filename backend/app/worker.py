import os
import zipfile
import tarfile
from redis import Redis
from rq import Worker, Queue
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static-analysis')))

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
        
        storage_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../storage"))
        storage_path = os.path.join(storage_base, f"projects/{project.id}")
        
        # We can extract features
        # We can extract features
        df, all_hotspots, skipped_files_list = analyze_directory(storage_path)
        features = df.to_dict('records')
        
        file_path_to_id = {}
        
        # All pending files in db
        pending_files = db.query(models.File).filter(models.File.project_id == project.id, models.File.status == "pending").all()
        pending_files_by_path = {os.path.abspath(os.path.join(storage_path, f.path)): f for f in pending_files}

        # Mark skipped files
        skipped_paths = set(os.path.abspath(p[0]) for p in skipped_files_list)
        
        for f_path, db_f in pending_files_by_path.items():
            if f_path in skipped_paths:
                db_f.status = "skipped"
            else:
                db_f.status = "analyzed"
            db.add(db_f)
            file_path_to_id[f_path] = db_f.id
        db.commit()

        # predict
        for feat in features:
            file_path = os.path.abspath(feat['file_path'])
            lang = feat['language']
            
            db_file_id = file_path_to_id.get(file_path)
            if not db_file_id:
                continue
                
            # predict
            pred_results = engine.predict([feat])
            if pred_results:
                p = pred_results[0]
                
                # Check for secrets
                if detect_secrets(file_path):
                    p['confidence_note'] = (p.get('confidence_note', '') + " | SECRET DETECTED").strip()
                    
                prediction = models.Prediction(
                    file_id=db_file_id,
                    run_id=run.id,
                    function_name=p['function_name'],
                    language=p['language'],
                    risk_score=p['risk_score'],
                    risk_level=p['risk_level'],
                    confidence_note=p['confidence_note'],
                    explanation_json=str(p['explanation'])
                )
                db.add(prediction)

        # Save hotspots
        for h in all_hotspots:
            h_path = os.path.abspath(h.get('file_path'))
            file_id = file_path_to_id.get(h_path)
            # If a file had hotspots but no functions, we already mapped it above because pending_files_by_path 
            # loaded all pending files. So file_id should be there.
            if not file_id:
                # Fallback just in case
                rel_path = os.path.relpath(h.get('file_path'), start=storage_path)
                db_file = db.query(models.File).filter(models.File.project_id == project.id, models.File.path == rel_path).first()
                if db_file:
                    file_id = db_file.id
                    file_path_to_id[h_path] = file_id
            
            if file_id:
                hotspot = models.Hotspot(
                    run_id=run.id,
                    file_id=file_id,
                    start_line=h.get('start_line'),
                    end_line=h.get('end_line'),
                    severity=h.get('severity'),
                    rule_id=h.get('rule_id'),
                    message=h.get('message')
                )
                db.add(hotspot)
                
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
