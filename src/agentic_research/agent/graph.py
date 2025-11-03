from __future__ import annotations
from typing import Dict, Any, List
from sqlmodel import Session
from ..tools import arxiv_search, summarize, github_repo

STAGES = [
    "Plan",
    "Search",
    "Extract",
    "Summarize",
    "Propose",
    "Scaffold",
    "Commit",
    "Report",
    "done",
]

class AgentGraph:
    def __init__(self, session: Session):
        self.session = session

    def run(self, task) -> str:
        state = task.state
        if state == "Plan":
            return "Search"
        if state == "Search":
            papers = arxiv_search.search(task.query, max_results=8)
            task.papers_json = arxiv_search.dump_json(papers)
            self.session.add(task); self.session.commit()
            return "Extract"
        if state == "Extract":
            # simple field normalization; you can add PDF parsing later
            return "Summarize"
        if state == "Summarize":
            # Summarize abstracts into bullets
            from json import loads, dumps
            papers = loads(task.papers_json or "[]")
            summary = summarize.summarize_text("\n\n".join(p.get("abstract","") for p in papers)[:8000])
            artifacts = [{"type": "summary", "content": summary}]
            task.artifacts_json = dumps(artifacts)
            self.session.add(task); self.session.commit()
            return "Propose"
        if state == "Propose":
            # naive next-steps proposal
            return "Scaffold" if task.scaffold_repo else "Report"
        if state == "Scaffold":
            scaffold = github_repo.generate_scaffold(task.query)
            task.artifacts_json = github_repo.append_artifact(task.artifacts_json, scaffold)
            self.session.add(task); self.session.commit()
            return "Commit"
        if state == "Commit":
            try:
                repo_url = github_repo.commit_scaffold(scaffold_env=None)  # reads env vars
            except Exception as e:
                repo_url = f"ERROR: {e}"
            task.artifacts_json = github_repo.append_artifact(task.artifacts_json, {"type": "repo", "url": repo_url})
            self.session.add(task); self.session.commit()
            return "Report"
        if state == "Report":
            return "done"
        return "done"
