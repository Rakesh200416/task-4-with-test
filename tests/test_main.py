from fastapi.testclient import TestClient
from uuid import uuid4

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app


client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_register_and_login_and_todos_crud():
    # make unique user each run
    uname = f"user_{uuid4().hex[:8]}"
    email = f"{uname}@test.com"
    password = "password123"

    # Register
    response = client.post("/register", json={
        "username": uname,
        "email": email,
        "password": password
    })
    assert response.status_code == 200

    # Login
    response = client.post("/login", data={
        "username": uname,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create Todo
    response = client.post("/todos/", headers=headers, json={
        "title": "First Todo",
        "description": "Testing todo"
    })
    assert response.status_code == 200
    todo = response.json()
    assert todo["title"] == "First Todo"
    todo_id = todo["id"]

    # List Todos
    response = client.get("/todos/", headers=headers)
    assert response.status_code == 200
    todos = response.json()
    assert any(t["id"] == todo_id for t in todos)

    # Update Todo
    response = client.put(f"/todos/{todo_id}", headers=headers, json={
        "title": "Updated Todo",
        "description": "Updated",
        "completed": True
    })
    assert response.status_code == 200
    updated = response.json()
    assert updated["title"] == "Updated Todo"
    assert updated["completed"] is True

    # Delete Todo
    response = client.delete(f"/todos/{todo_id}", headers=headers)
    assert response.status_code == 200
