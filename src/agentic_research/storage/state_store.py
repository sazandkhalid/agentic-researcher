from sqlmodel import Session, SQLModel, Field, create_engine
from datetime import datetime
from typing import Optional
import json
from ..config import settings

_engine = create_engine(settings.DB_URL, echo=False)

class GraphCheckpoint(SQLModel, table=True):
    id: str = Field(primary_key=True)
    task_id: str
    state_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

def save_checkpoint(session: Session, task_id: str, state: dict):
    cp = GraphCheckpoint(
        id=f"{task_id}-{int(datetime.utcnow().timestamp())}",
        task_id=task_id,
        state_json=json.dumps(state)
    )
    session.add(cp)
    session.commit()

def load_latest_checkpoint(session: Session, task_id: str) -> Optional[dict]:
    res = session.exec(
        f"SELECT state_json FROM graphcheckpoint WHERE task_id='{task_id}' ORDER BY created_at DESC LIMIT 1"
    ).first()
    if not res:
        return None
    return json.loads(res)
