import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_flow():
    # 1. Register
    username = f"testuser_{int(time.time())}"
    print(f"Registering {username}...")
    r = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": "password"})
    assert r.status_code == 200, f"Register failed: {r.text}"
    token = r.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Login (just to verify)
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": username, "password": "password"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    
    # 3. Create a project
    print("Creating project...")
    # Make a dummy python file
    with open("test_file.py", "w") as f:
        f.write("password = '123'\nprint(password)\n")
        
    with open("test_file.py", "rb") as f:
        r = requests.post(
            f"{BASE_URL}/projects",
            headers=headers,
            data={"name": "Test Project"},
            files={"file": ("test_file.py", f, "text/x-python")}
        )
    assert r.status_code == 200, f"Create project failed: {r.text}"
    project_id = r.json()["id"]
    print(f"Project created: {project_id}")
    
    # Wait a bit for analysis if it's synchronous it might already be done, but /projects/{id}/analyze does it.
    # Actually wait, /projects in backend does analysis right away? No, it calls /analyze explicitly from frontend.
    print("Starting analysis...")
    r = requests.post(f"{BASE_URL}/projects/{project_id}/analyze", headers=headers)
    assert r.status_code == 200, f"Analyze failed: {r.text}"
    run_id = r.json()["run_id"]
    print(f"Analysis started: {run_id}")
    
    # 4. Wait for completion
    while True:
        r = requests.get(f"{BASE_URL}/analysis/{run_id}/status", headers=headers)
        status = r.json()["status"]
        print(f"Status: {status}")
        if status in ["completed", "failed", "analyzed"]:
            break
        time.sleep(1)
        
    # 5. View results
    r = requests.get(f"{BASE_URL}/projects/{project_id}/files", headers=headers)
    assert r.status_code == 200
    files = r.json()["files"]
    print(f"Files: {files}")
    file_id = files[0]["id"]
    
    r = requests.get(f"{BASE_URL}/files/{file_id}/source", headers=headers)
    assert r.status_code == 200
    
    r = requests.get(f"{BASE_URL}/files/{file_id}/annotations?run_id={run_id}", headers=headers)
    assert r.status_code == 200
    print(f"Annotations: {r.json()}")
    
    print("ALL E2E TESTS PASSED!")

if __name__ == "__main__":
    test_flow()
