from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pydantic import BaseModel
from ..config import settings

_engine = create_engine(settings.DB_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(_engine)

class SessionDep:
    def __enter__(self):
        self.session = Session(_engine)
        return self.session
    def __exit__(self, exc_type, exc, tb):
        self.session.close()

class Task(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    query: str
    status: str = "pending"   # pending, running, done, failed
    state: str = "Plan"       # current stage label
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    scaffold_repo: bool = True
    artifacts_json: str = "[]"  # list of dicts
    papers_json: str = "[]"     # list of dicts

    def to_dict(self) -> Dict[str, Any]:
        import json
        return {
            "id": self.id,
            "query": self.query,
            "status": self.status,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "scaffold_repo": self.scaffold_repo,
            "artifacts": json.loads(self.artifacts_json or "[]"),
            "papers": json.loads(self.papers_json or "[]"),
        }

class TaskCreate(BaseModel):
    query: str
    scaffold_repo: bool = True

def create_task(session: Session, data: TaskCreate) -> Task:
    task = Task(query=data.query, scaffold_repo=data.scaffold_repo)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_task(session: Session, task_id: str) -> Optional[Task]:
    return session.get(Task, task_id)

def update_task_state(session: Session, task: Task, new_state: str):
    from datetime import datetime
    task.state = new_state
    task.status = "running" if new_state not in ("done", "failed") else new_state
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
