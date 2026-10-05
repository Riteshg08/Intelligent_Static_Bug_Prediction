import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import zipfile
import shutil
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../static-analysis')))

from app.main import app, limiter
from app.database import get_db, Base
from app.models import User, Project, AnalysisRun, Prediction

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_hardening.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_hardening.db"):
        os.remove("./test_hardening.db")

@pytest.fixture
def test_user():
    response = client.post("/api/v1/auth/register", json={"username": "testuser", "password": "password"})
    if response.status_code != 200:
        response = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "password"})
    return response.json()["access_token"]

@pytest.fixture
def test_user2():
    response = client.post("/api/v1/auth/register", json={"username": "otheruser", "password": "password"})
    if response.status_code != 200:
        response = client.post("/api/v1/auth/login", data={"username": "otheruser", "password": "password"})
    return response.json()["access_token"]

def test_auth_failure(test_user, test_user2):
    # Create project with test_user
    res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {test_user}"},
        data={"name": "AuthTestProject"},
        files={"file": ("test.py", b"print('hello')")}
    )
    assert res.status_code == 200
    project_id = res.json()["id"]

    # Try to access it with test_user2
    res2 = client.get(
        f"/api/v1/projects/{project_id}/files",
        headers={"Authorization": f"Bearer {test_user2}"}
    )
    assert res2.status_code == 404

def test_malicious_zip(test_user):
    import io
    
    # Create a malicious zip with absolute path
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr("/etc/passwd", "root:x:0:0:root:/root:/bin/bash")
        
    zip_buffer.seek(0)
    
    res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {test_user}"},
        data={"name": "MaliciousZip"},
        files={"file": ("malicious.zip", zip_buffer.read())}
    )
    assert res.status_code == 400
    assert "slip" in res.json()["detail"].lower()

def test_oversized_upload(test_user):
    os.environ["MAX_UPLOAD_SIZE"] = "100" # 100 bytes
    large_content = b"a" * 200
    
    res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {test_user}"},
        data={"name": "Oversized"},
        files={"file": ("large.py", large_content)}
    )
    assert res.status_code == 413
    assert "too large" in res.json()["detail"].lower()
    os.environ.pop("MAX_UPLOAD_SIZE")

def test_feedback_round_trip(test_user):
    # Create a project and file
    res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {test_user}"},
        data={"name": "FeedbackTest"},
        files={"file": ("test.py", b"def foo():\n    pass\n")}
    )
    assert res.status_code == 200
    project_id = res.json()["id"]

    db = TestingSessionLocal()
    run = AnalysisRun(project_id=project_id, status="completed")
    db.add(run)
    db.commit()
    
    from app.models import File
    file_obj = db.query(File).filter(File.project_id == project_id).first()
    
    pred = Prediction(
        file_id=file_obj.id,
        run_id=run.id,
        function_name="foo",
        language="Python",
        risk_score=0.9,
        risk_level="High"
    )
    db.add(pred)
    db.commit()
    
    pred_id = pred.id
    db.close()

    # Submit feedback
    feedback_data = {"is_real_bug": True, "comment": "This is a real bug"}
    res = client.post(
        f"/api/v1/predictions/{pred_id}/feedback",
        headers={"Authorization": f"Bearer {test_user}"},
        json=feedback_data
    )
    assert res.status_code == 200

    # Get feedback
    res = client.get(
        f"/api/v1/predictions/{pred_id}/feedback",
        headers={"Authorization": f"Bearer {test_user}"}
    )
    assert res.status_code == 200
    assert res.json()["is_real_bug"] == True
    assert res.json()["comment"] == "This is a real bug"

def test_worker_end_to_end(test_user):
    # Create a project with sample_buggy_code.py
    with open("sample_buggy_code.py", "rb") as f:
        content = f.read()
        
    res = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {test_user}"},
        data={"name": "WorkerTest"},
        files={"file": ("sample_buggy_code.py", content)}
    )
    assert res.status_code == 200
    project_id = res.json()["id"]
    
    # Run analysis
    res = client.post(
        f"/api/v1/projects/{project_id}/analyze",
        headers={"Authorization": f"Bearer {test_user}"}
    )
    assert res.status_code == 200
    run_id = res.json()["run_id"]
    
    # Check status
    import time
    for _ in range(10):
        res = client.get(
            f"/api/v1/analysis/{run_id}/status",
            headers={"Authorization": f"Bearer {test_user}"}
        )
        if res.json()["status"] == "completed":
            break
        time.sleep(0.5)
        
    assert res.json()["status"] == "completed"
    assert res.json()["files_total"] == 1
    assert res.json()["files_done"] == 1
    
    # Get files
    res = client.get(
        f"/api/v1/analysis/{run_id}/files",
        headers={"Authorization": f"Bearer {test_user}"}
    )
    assert res.status_code == 200
    assert len(res.json()) > 0
    
    # Get predictions
    res = client.get(
        f"/api/v1/analysis/{run_id}/predictions",
        headers={"Authorization": f"Bearer {test_user}"}
    )
    assert res.status_code == 200
    assert len(res.json()) > 0
