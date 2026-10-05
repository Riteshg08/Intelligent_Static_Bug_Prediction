import os
import json
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

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "sbp_tasks")
redis_conn = Redis.from_url(REDIS_URL)
task_queue = Queue(QUEUE_NAME, connection=redis_conn)

default_models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models"))
models_dir = os.path.abspath(os.getenv("MODELS_DIR", default_models_dir))
engine = PredictionEngine(models_dir=models_dir)
default_storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../storage"))
STORAGE_DIR = os.path.abspath(os.getenv("STORAGE_DIR", default_storage_dir))
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
        
        storage_path = os.path.join(STORAGE_DIR, f"projects/{project.id}")
        
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
        
        run.files_total = len(pending_files_by_path)
        run.files_skipped = len(skipped_paths)
        run.skipped_reasons = json.dumps({p[0]: p[1] for p in skipped_files_list})
        db.commit()

        print(f"DEBUG: Found {len(features)} features")
        # predict
        for feat in features:
            file_path = os.path.abspath(feat['file_path'])
            lang = feat['language']
            print(f"DEBUG: Checking {file_path}")
            
            db_file_id = file_path_to_id.get(file_path)
            if not db_file_id:
                print(f"DEBUG: {file_path} not in file_path_to_id!")
                continue
                
            # predict
            pred_results = engine.predict([feat])
            print(f"DEBUG: predict results: {pred_results}")
            if pred_results:
                p = pred_results[0]
                
                # Check for secrets
                secret_detected = detect_secrets(file_path)
                
                # Check for high severity hotspots in this function
                # We need to filter all_hotspots by file and line range
                func_start = p.get('start_line', 0)
                func_end = p.get('end_line', 99999)
                
                func_hotspots = [
                    h for h in all_hotspots 
                    if h.get('file_path') == feat['file_path'] 
                    and h.get('severity') == 'high'
                    and h.get('start_line', 0) >= func_start
                    and h.get('end_line', 99999) <= func_end
                ]
                
                if secret_detected or func_hotspots:
                    p['risk_score'] = max(p['risk_score'], 0.95)
                    p['risk_level'] = "High"
                    p['confidence_note'] = (p.get('confidence_note', '') + " | CRITICAL STATIC FINDING").strip()
                    p['explanation'].insert(0, "Static analysis detected a high-risk pattern in this function.")
                    
                prediction = models.Prediction(
                    file_id=db_file_id,
                    run_id=run.id,
                    function_name=p['function_name'],
                    start_line=p.get('start_line'),
                    end_line=p.get('end_line'),
                    language=p['language'],
                    risk_score=p['risk_score'],
                    risk_level=p['risk_level'],
                    confidence_note=p['confidence_note'],
                    explanation_json=json.dumps(p['explanation'])
                )
                db.add(prediction)
                run.functions_found += 1
            
            # Incremental updates per feature loop is too granular, let's update per file if needed
            # Actually, `features` is a list of functions, we can just commit periodically or at the end
            db.commit()

        # Save hotspots
        for h in all_hotspots:
            h_path = os.path.abspath(h.get('file_path'))
            file_id = file_path_to_id.get(h_path)
            if not file_id:
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
        run.files_done = len(file_path_to_id) - run.files_skipped
        db.commit()
    except Exception as e:
        run = db.query(models.AnalysisRun).filter(models.AnalysisRun.id == run_id).first()
        if run:
            run.status = "failed"
            run.error_message = str(e)
            db.commit()
        print(f"Error in analysis: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    worker = Worker([task_queue], connection=redis_conn)
    worker.work()
