# FastAPI Basics

A basic practice project for learning FastAPI with SQLModel and PostgreSQL. Implements a simple Task CRUD API.

## Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/) (SQLAlchemy + Pydantic)
- PostgreSQL

## Project Structure

- `main.py` — FastAPI app and route definitions
- `models.py` — SQLModel `Task` table definition
- `database.py` — DB engine and session dependency

## Setup

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn sqlmodel psycopg2-binary
   ```

2. Make sure PostgreSQL is running and update the connection string in `database.py` if needed:
   ```python
   DATABASE_URL = "postgresql://postgres:ped@localhost/test_db"
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

4. Open the interactive docs at `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Path              | Description       |
|--------|-------------------|--------------------|
| POST   | `/tasks`          | Create a task      |
| GET    | `/tasks`          | List all tasks     |
| GET    | `/tasks/{task_id}`| Get a single task  |
| PUT    | `/tasks/{task_id}`| Update a task      |
| DELETE | `/tasks/{task_id}`| Delete a task      |

## Task Model

```python
{
  "id": int,
  "title": str,
  "description": str | None,
  "completed": bool,
  "priority": int
}
```
