from sqlmodel import SQLModel, Field


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    title: str
    description: str | None = None
    completed: bool = False
    priority: int