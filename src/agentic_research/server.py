from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .storage.db import init_db, SessionDep, Task, TaskCreate, get_task, create_task, update_task_state
from .agent.graph import AgentGraph

app = FastAPI(title="Agentic Research Assistant")
init_db()

class CreateTaskReq(BaseModel):
    query: str
    scaffold_repo: bool = True

@app.post("/tasks")
def create_task_ep(req: CreateTaskReq):
    with SessionDep() as session:
        task = create_task(session, TaskCreate(query=req.query, scaffold_repo=req.scaffold_repo))
        return JSONResponse({"task_id": task.id, "status": task.status})

@app.get("/tasks/{task_id}")
def get_task_ep(task_id: str):
    with SessionDep() as session:
        task = get_task(session, task_id)
        if not task:
            raise HTTPException(404, "Task not found")
        return task.to_dict()

@app.post("/run/{task_id}")
def run_task_ep(task_id: str):
    with SessionDep() as session:
        task = get_task(session, task_id)
        if not task:
            raise HTTPException(404, "Task not found")
        graph = AgentGraph(session=session)
        new_state = graph.run(task)
        update_task_state(session, task, new_state)
        return {"task_id": task.id, "state": new_state}
