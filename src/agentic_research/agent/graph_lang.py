from ..storage.state_store import save_checkpoint
import time

# ✅ SEARCH NODE with checkpoint and error handling
def search_node(state: AgentState, session=None, task_id=None) -> AgentState:
    try:
        papers = arxiv_search.search(state["query"], max_results=8)
        state["papers"] = papers
        state["stage"] = "Extract"
        state.pop("error", None)
    except Exception as e:
        state["error"] = str(e)
        state["prev_stage"] = "Search"
        state["stage"] = "Error"

    # ✅ Save progress
    if session and task_id:
        state = checkpoint_node(session, task_id, state)

    return state


# ✅ CHECKPOINT NODE HELPER
def checkpoint_node(session, task_id, new_state: AgentState) -> AgentState:
    """Save graph progress to the database."""
    try:
        save_checkpoint(session, task_id, new_state)
    except Exception as e:
        print(f"[WARN] Failed to checkpoint state: {e}")
    return new_state


# ✅ ERROR NODE WITH RETRIES
def error_node(state: AgentState) -> AgentState:
    """Handle transient errors with exponential backoff and retry."""
    attempt = state.get("attempt", 0) + 1
    state["attempt"] = attempt

    if attempt > 3:
        state["stage"] = "failed"
        print(f"[ERROR] Too many retries: {state.get('error')}")
        return state

    wait = 2 ** attempt
    print(f"[WARN] Error occurred: {state.get('error')} → retrying {state.get('prev_stage')} in {wait}s")
    time.sleep(wait)

    # retry previous stage
    prev = state.get("prev_stage", "Search")
    state["stage"] = prev
    return state
