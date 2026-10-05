import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app.models import User, Project, AnalysisRun, File
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create users
    u1 = User(username="user1", hashed_password="pw1")
    u2 = User(username="user2", hashed_password="pw2")
    db.add_all([u1, u2])
    db.commit()
    db.refresh(u1)
    db.refresh(u2)
    
    # Create project for user1
    p1 = Project(name="Project1", owner_id=u1.id)
    db.add(p1)
    db.commit()
    db.refresh(p1)
    
    run = AnalysisRun(project_id=p1.id, status="completed")
    db.add(run)
    db.commit()
    db.refresh(run)
    
    f1 = File(project_id=p1.id, path="test.py", language="Python")
    db.add(f1)
    db.commit()
    db.refresh(f1)
    
    yield {"u1": u1, "u2": u2, "p1": p1, "run": run, "f1": f1}
    
    Base.metadata.drop_all(bind=engine)

def test_unauthenticated_access(setup_db):
    response = client.get(f"/api/v1/analysis/{setup_db['run'].id}/files")
    assert response.status_code == 401

def test_unauthorized_access_to_others_project(setup_db):
    from app.main import create_access_token
    # Login as user2
    token = create_access_token(data={"sub": setup_db['u2'].username})
    headers = {"Authorization": f"Bearer {token}"}
    
    # User 2 tries to access User 1's project analysis files
    response = client.get(f"/api/v1/analysis/{setup_db['run'].id}/files", headers=headers)
    assert response.status_code == 404 # Our app returns 404 when project doesn't belong to user
    
    # User 2 tries to access User 1's file source
    response = client.get(f"/api/v1/files/{setup_db['f1'].id}/source", headers=headers)
    assert response.status_code == 404
