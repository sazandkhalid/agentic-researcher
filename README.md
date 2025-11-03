# Agentic Research Assistant (Starter)

An end-to-end **agentic AI** project that executes multi-step research workflows:
1) Search recent papers (arXiv), 
2) extract methods/baselines/datasets, 
3) recommend directions, 
4) scaffold a PyTorch repo, and 
5) track progress with tasks — all with **human-in-the-loop** approvals.

## Features (MVP)
- **FastAPI** server (`/tasks`, `/run`) for kicking off jobs and checking status
- **Agent graph** with deterministic stages: *Plan → Search → Extract → Summarize → Propose → Scaffold → Commit → Report*
- **Tools**: `arxiv_search`, `summarize` (LLM-agnostic), `github_repo` (create repo & commit scaffold), `tasks` (Trello/Notion stub)
- **Storage**: SQLite via **SQLModel** for Tasks, Papers, Runs and Artifacts
- **Evals**: simple harness to log latencies and success metrics
- **Config** via pydantic Settings (env vars)
- **Dockerfile** for containerization + `make dev` to run locally

> This repo is intentionally **framework-light**. You can swap in LangGraph, Guardrails, or your preferred planner without changing the API shape.

## Quickstart

```bash
# 1) Clone & enter
# (after you download the zip below)
uv venv && source .venv/bin/activate   # or: python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2) Set environment
cp .env.example .env
# fill GITHUB_TOKEN if you want repo creation

# 3) Run API
uvicorn agentic_research.server:app --reload

# 4) Create a task
curl -XPOST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{
  "query": "agentic reinforcement learning recent papers baseline methods",
  "scaffold_repo": true
}'
```

### Endpoints

- `POST /tasks` — create a research task
- `GET  /tasks/{task_id}` — fetch task + latest state
- `POST /run/{task_id}` — run/continue the agent for a task (idempotent stages)

### Environment (.env)

```
# Optional but needed for GitHub actions
GITHUB_TOKEN=ghp_...

# Optional: LLM provider settings (use your own)
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# SQLite file path
DB_URL=sqlite:///./agent.db
```

### Minimal System Diagram

```
FastAPI
  ├─ POST /tasks  → DB.Task (pending)
  ├─ POST /run    → AgentGraph(state) → tools/* → DB updates (papers, artifacts)
  └─ GET  /tasks/:id → status

AgentGraph Stages:
  Plan → Search(arXiv) → Extract(parse) → Summarize(LLM or heuristic) →
  Propose(next steps) → Scaffold(code) → Commit(GitHub) → Report(artifacts)
```

---

## What to extend
- Replace `summarize.summarize_text` with your LLM client (OpenAI/Anthropic)
- Add `LangGraph` for step-level retries and guardrails
- Implement `tools/tasks.py` to push tasks to Trello/Notion
- Replace `arxiv_search` ranker with your own relevance + recency scoring
- Add vector store for long-term memory (pgvector/FAISS); hook into `storage`
- Add validation datasets + eval dashboards (Prometheus + Grafana or OpenTelemetry)

---

## License
MIT
