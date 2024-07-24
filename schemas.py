from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    id: int
    task_name: str
    description: str
    create_time: datetime
    deadline: datetime
    done: bool
    user_id: int


class TaskUpdate(BaseModel):
    task_name: str | None
    description: str | None
    deadline: datetime | None
    user_id: int | None
