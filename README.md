# Todo API (FastAPI) — Task 4 (Tests + CI)

Endpoints:
- `GET /` → `{"message": "Hello World"}`
- `POST /register` → create or return existing user
- `POST /login` (form data) → returns access token
- `POST /todos/` (auth) → create todo
- `GET /todos/` (auth) → list todos
- `PUT /todos/{id}` (auth) → update todo
- `DELETE /todos/{id}` (auth) → delete todo

Run locally:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Run tests:
```bash
pytest -v
```

Docker:
```bash
docker build -t todo-api .
docker run -p 8000:8000 --env-file .env todo-api
# or with compose
docker-compose up --build
```
