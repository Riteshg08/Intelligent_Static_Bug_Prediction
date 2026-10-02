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
def auth_token():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    client.post("/api/v1/auth/register", json={"username": "testuser", "password": "testpassword"})
    response = client.post("/api/v1/auth/login", data={"username": "testuser", "password": "testpassword"})
    return response.json()["access_token"]

def test_project_upload(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"def test_func():\n    pass")
        temp_name = f.name
        
    with open(temp_name, "rb") as f:
        response = client.post("/api/v1/projects", data={"name": "Test Project"}, files={"file": ("test.py", f, "text/plain")}, headers=headers)
        
    assert response.status_code == 200
    assert "id" in response.json()
    
from unittest.mock import patch
from app.main import task_queue

@patch.object(task_queue, "enqueue")
def test_analyze_project(mock_enqueue, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Create project
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(b"def test_func():\n    pass")
        temp_name = f.name
        
    with open(temp_name, "rb") as f:
        response = client.post("/api/v1/projects", data={"name": "Test Project"}, files={"file": ("test.py", f, "text/plain")}, headers=headers)
        
    project_id = response.json()["id"]
    
    # Trigger analyze
    response = client.post(f"/api/v1/projects/{project_id}/analyze", headers=headers)
    assert response.status_code == 200
    assert "run_id" in response.json()
    run_id = response.json()["run_id"]
    
    # Get status
    response = client.get(f"/api/v1/analysis/{run_id}/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
