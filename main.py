from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Annotated
from sqlmodel import SQLModel, Session, select
from models import Task

# app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False
    priority: int | None = None

# class TaskResponse(BaseModel):
#     id: int
#     title: str
#     description: str | None = None
#     completed: bool = False
#     priority: int | None = None

# tasks = []
# @app.get("/tasks", response_model=list[TaskResponse])
# def read_tasks():
#     # Placeholder implementation - replace with actual task retrieval logic
#     return tasks

# @app.post("/tasks", response_model=TaskResponse)
# def create_task(task: TaskCreate):
#     # Placeholder implementation - replace with actual task creation logic
#     new_task = TaskResponse(id=len(tasks) + 1, **task.dict())
#     tasks.append(new_task)
#     return new_task

# @app.get("/tasks/{task_id}", response_model=TaskResponse)
# def read_task(task_id: int):
#     # Placeholder implementation - replace with actual task retrieval logic
#     for task in tasks:
#         if task.id == task_id:
#             return task
#     raise HTTPException(status_code=404, detail="Task not found")

# @app.put("/tasks/{task_id}", response_model=TaskResponse)
# def update_task(task_id: int, task: TaskCreate):
#     for i, existing_task in enumerate(tasks):
#         if existing_task.id == task_id:
#             updated_task = TaskResponse(id=task_id, **task.dict())
#             tasks[i] = updated_task
#             return updated_task

#     raise HTTPException(status_code=404, detail="Task not found")

# @app.delete("/tasks/{task_id}", response_model=dict)
# def delete_task(task_id: int):
#     for i, existing_task in enumerate(tasks):
#         if existing_task.id == task_id:
#             del tasks[i]
#             return {"message": "Task deleted successfully"}

#     raise HTTPException(status_code=404, detail="Task not found")


# def get_pagination(
#     page: int = Query(1, ge=1, description="Page number, starting at 1"),
#     limit: int = Query(10, ge=1, le=100, description="Items per page, 1-100"),
# ) -> dict:
#     return {"page": page, "limit": limit, "offset": (page - 1) * limit}

# @app.get("/products")
# def get_products(
#     pagination = Depends(get_pagination)
# ):
#     # Placeholder implementation - replace with actual product retrieval logic
#     products = [
#         {"id": 1, "name": "Product 1"},
#         {"id": 2, "name": "Product 2"},
#         {"id": 3, "name": "Product 3"},
#         # Add more products as needed
#     ]
#     start = pagination["offset"]
#     end = start + pagination["limit"]
#     return products[start:end]

# def get_current_user():
#     return {
#           "id": 1,
#          "name": "Haris",
#          "role": "admin"
#     }

# @app.delete("/products/{product_id}")
# def delete_product(product_id: int, current_user = Depends(get_current_user)):
#     if current_user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized to delete products")
    
#     # Placeholder implementation - replace with actual product deletion logic
#     return {"message": f"Product {product_id} deleted successfully"}


from database import engine, get_session

app = FastAPI()


@app.on_event("startup")
def create_tables():
    SQLModel.metadata.create_all(engine)


@app.post("/tasks")
def create_task(
    task: Task,
    session: Session = Depends(get_session)
):
    session.add(task)
    session.commit()
    session.refresh(task)

    return task

@app.get("/tasks")
def read_tasks(
    session: Session = Depends(get_session)
):
    tasks = session.exec(select(Task)).all()
    return tasks

@app.get("/tasks/{task_id}")
def read_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: Task,
    session: Session = Depends(get_session)
):
    existing_task = session.exec(select(Task).where(Task.id == task_id)).first()
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in task.dict(exclude_unset=True).items():
        setattr(existing_task, field, value)

    session.commit()
    session.refresh(existing_task)
    return existing_task

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}