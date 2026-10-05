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
QUEUE_NAME = os.getenv("QUEUE_NAME", "analysis")
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
        
        def norm_path(p):
            import pathlib
            return str(pathlib.Path(p).resolve()).lower()
            
        # All pending files in db
        pending_files = db.query(models.File).filter(models.File.project_id == project.id, models.File.status == "pending").all()
        pending_files_by_path = {norm_path(os.path.join(storage_path, f.path)): f for f in pending_files}

        # Mark skipped files
        skipped_paths = set(norm_path(p[0]) for p in skipped_files_list)
        
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

        from collections import defaultdict
        features_by_file = defaultdict(list)
        for feat in features:
            features_by_file[norm_path(feat['file_path'])].append(feat)
            
        print(f"DEBUG: Found {len(features)} features across {len(features_by_file)} files")
        # predict
        for file_path, file_features in features_by_file.items():
            print(f"DEBUG: Checking {file_path}")
            
            db_file_id = file_path_to_id.get(file_path)
            if not db_file_id:
                print(f"DEBUG: {file_path} not in file_path_to_id!")
                continue
                
            # predict in batch for the file
            pred_results = engine.predict(file_features)
            
            # Check for secrets once for the file
            secret_detected = detect_secrets(file_path)
            
            for feat, p in zip(file_features, pred_results):
                if "error" in p:
                    print(f"DEBUG: Predict error: {p['error']}")
                    continue
                    
                # Calculate pattern severity
                func_start = p.get('start_line', 0)
                func_end = p.get('end_line', 99999)
                
                func_hotspots = [
                    h for h in all_hotspots 
                    if norm_path(h.get('file_path', '')) == file_path 
                    and h.get('start_line', 0) >= func_start
                    and h.get('end_line', 99999) <= func_end
                ]
                
                pattern_severity = "none"
                if secret_detected:
                    pattern_severity = "1 high"
                elif func_hotspots:
                    high_count = sum(1 for h in func_hotspots if h.get('severity') == 'high')
                    warn_count = sum(1 for h in func_hotspots if h.get('severity') == 'warning')
                    info_count = sum(1 for h in func_hotspots if h.get('severity') == 'info')
                    
                    if high_count > 0:
                        pattern_severity = f"{high_count} high"
                    elif warn_count > 0:
                        pattern_severity = f"{warn_count} warning"
                    else:
                        pattern_severity = f"{info_count} info"
                    
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
                    explanation_json=json.dumps(p['explanation']),
                    pattern_severity=pattern_severity
                )
                db.add(prediction)
                run.functions_found += 1
            
            # Commit per file
            db.commit()

        # Save hotspots
        for h in all_hotspots:
            h_path = norm_path(h.get('file_path'))
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
