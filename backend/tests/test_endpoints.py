import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "testsecret"

from app.main import app
from app.database import Base, get_db
from app import models

engine = create_engine(
    os.environ["DATABASE_URL"], connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def auth_token(test_db):
    client.post("/api/v1/auth/register", json={"username": "testuser", "password": "testpassword"})
    response = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "testpassword"})
    return response.json()["access_token"]

@pytest.fixture
def auth_token2(test_db):
    client.post("/api/v1/auth/register", json={"username": "otheruser", "password": "testpassword"})
    response = client.post("/api/v1/auth/login", data={"username": "otheruser", "password": "testpassword"})
    return response.json()["access_token"]

def test_export_analysis(auth_token, auth_token2, test_db):
    headers = {"Authorization": f"Bearer {auth_token}"}
    headers2 = {"Authorization": f"Bearer {auth_token2}"}
    
    # 401 Unauthenticated
    resp = client.get("/api/v1/analysis/999/export")
    assert resp.status_code == 401
    
    # Create project and run
    user1 = test_db.query(models.User).filter_by(username="testuser").first()
    proj = models.Project(name="Proj", owner_id=user1.id)
    test_db.add(proj)
    test_db.commit()
    
    run = models.AnalysisRun(project_id=proj.id, status="completed")
    test_db.add(run)
    test_db.commit()
    
    file = models.File(project_id=proj.id, path="test.py", language="Python", status="analyzed")
    test_db.add(file)
    test_db.commit()
    
    pred = models.Prediction(file_id=file.id, run_id=run.id, function_name="func1", language="Python", risk_score=0.9, risk_level="high")
    test_db.add(pred)
    test_db.commit()

    # Success
    resp = client.get(f"/api/v1/analysis/{run.id}/export", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["findings"]) == 1
    assert data["findings"][0]["function"] == "func1"

    # 403/404 Not owned (user2)
    resp2 = client.get(f"/api/v1/analysis/{run.id}/export", headers=headers2)
    assert resp2.status_code == 404
    
def test_submit_feedback_ownership(auth_token, auth_token2, test_db):
    headers = {"Authorization": f"Bearer {auth_token}"}
    headers2 = {"Authorization": f"Bearer {auth_token2}"}
    
    user1 = test_db.query(models.User).filter_by(username="testuser").first()
    proj = models.Project(name="Proj2", owner_id=user1.id)
    test_db.add(proj)
    test_db.commit()
    
    file = models.File(project_id=proj.id, path="test.py", language="Python")
    test_db.add(file)
    test_db.commit()
    
    pred = models.Prediction(file_id=file.id, run_id=1, function_name="func", language="Python", risk_score=0.9)
    test_db.add(pred)
    test_db.commit()
    
    # Other user shouldn't be able to submit feedback on testuser's project
    resp = client.post(f"/api/v1/predictions/{pred.id}/feedback?is_real_bug=true", headers=headers2)
    assert resp.status_code == 403
    
    # Owner should succeed
    resp = client.post(f"/api/v1/predictions/{pred.id}/feedback?is_real_bug=true", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "saved"
    
def test_analysis_status_by_language(auth_token, auth_token2, test_db):
    headers = {"Authorization": f"Bearer {auth_token}"}
    headers2 = {"Authorization": f"Bearer {auth_token2}"}
    
    user1 = test_db.query(models.User).filter_by(username="testuser").first()
    proj = models.Project(name="Proj", owner_id=user1.id)
    test_db.add(proj)
    test_db.commit()
    
    run = models.AnalysisRun(project_id=proj.id, status="completed")
    test_db.add(run)
    test_db.commit()
    
    test_db.add(models.File(project_id=proj.id, path="test.py", language="Python", status="analyzed"))
    test_db.add(models.File(project_id=proj.id, path="test2.py", language="Python", status="failed"))
    test_db.add(models.File(project_id=proj.id, path="app.js", language="JavaScript", status="analyzed"))
    test_db.commit()
    
    resp = client.get(f"/api/v1/analysis/{run.id}/status/languages", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["Python"]["total"] == 2
    assert data["Python"]["analyzed"] == 1
    assert data["Python"]["failed"] == 1
    assert data["JavaScript"]["total"] == 1
    assert data["JavaScript"]["analyzed"] == 1
    
    resp2 = client.get(f"/api/v1/analysis/{run.id}/status/languages", headers=headers2)
    assert resp2.status_code == 404
