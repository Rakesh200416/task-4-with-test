from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.database import Base, engine
from app import models, schemas
from app.auth import get_db, get_password_hash, create_access_token, authenticate_user, get_current_user

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API")

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Hello World"}

# ---------- Auth ----------
@app.post("/register", response_model=schemas.UserRead, tags=["auth"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Idempotent registration to keep tests repeatable
    existing = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if existing:
        return existing  # Return existing user (status 200)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token, tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ---------- Todos ----------
@app.post("/todos/", response_model=schemas.TodoRead, tags=["todos"])
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_todo = models.Todo(title=todo.title, description=todo.description or "", owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

@app.get("/todos/", response_model=List[schemas.TodoRead], tags=["todos"])
def list_todos(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    todos = db.query(models.Todo).filter(models.Todo.owner_id == current_user.id).order_by(models.Todo.id).all()
    return todos

@app.put("/todos/{todo_id}", response_model=schemas.TodoRead, tags=["todos"])
def update_todo(todo_id: int, updates: schemas.TodoUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if updates.title is not None:
        todo.title = updates.title
    if updates.description is not None:
        todo.description = updates.description
    if updates.completed is not None:
        todo.completed = updates.completed
    db.commit()
    db.refresh(todo)
    return todo

@app.delete("/todos/{todo_id}", tags=["todos"])
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id, models.Todo.owner_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"detail": "Deleted"}
