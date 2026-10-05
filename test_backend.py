import requests
import json
import os
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

# 1. Register
session = requests.Session()
register_res = session.post(f"{BASE_URL}/auth/register", json={"username": "testuser", "password": "testpassword123"})
print("Register:", register_res.status_code, register_res.text)

# 2. Login
login_res = session.post(f"{BASE_URL}/auth/login", data={"username": "testuser", "password": "testpassword123"})
print("Login:", login_res.status_code, login_res.text)

token = login_res.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

# 3. Upload real_bugs_sample.py
with open("real_bugs_sample.py", "rb") as f:
    files = {"file": ("real_bugs_sample.py", f, "text/x-python")}
    upload_res = session.post(f"{BASE_URL}/projects", headers=headers, data={"name": "Test Project"}, files=files)
    print("Upload:", upload_res.status_code, upload_res.text)

project_id = upload_res.json()["id"]

# 4. Get files
files_res = session.get(f"{BASE_URL}/projects/{project_id}/files", headers=headers)
print("Files:", files_res.status_code, files_res.text)
files_list = files_res.json()["files"]

for f in files_list:
    file_id = f["id"]
    path = f["path"]
    
    # 5. Get source
    source_res = session.get(f"{BASE_URL}/files/{file_id}/source", headers=headers)
    print(f"Source for {path} (id={file_id}):", source_res.status_code)
    
    # 6. Analyze
    analyze_res = session.post(f"{BASE_URL}/projects/{project_id}/analyze", headers=headers)
    print(f"Analyze project:", analyze_res.status_code, analyze_res.text)
    
    run_id = analyze_res.json()["run_id"]
    
    # Poll status
    for i in range(10):
        time.sleep(1)
        status_res = session.get(f"{BASE_URL}/analysis/{run_id}/status", headers=headers)
        status = status_res.json()["status"]
        print("Status:", status)
        if status in ["completed", "failed"]:
            break
            
    # Get annotations
    ann_res = session.get(f"{BASE_URL}/files/{file_id}/annotations?run_id={run_id}", headers=headers)
    print("Annotations:", ann_res.status_code, ann_res.text)
