from .llm import llm_summary_request

def summarize_text(text: str, max_bullets: int = 8) -> str:
    """
    Try OpenAI summarization. If missing key or failure,
    fall back to rule-based bullet extraction.
    """
    # Attempt LLM call
    prompt = f"Summarize the following research abstracts into ~{max_bullets} key bullet points:\n\n{text}\n\nFormat:\n- Key idea\n- Methods\n- Baselines\n- Dataset\n- Contribution"
    llm_result = llm_summary_request(prompt)

    if llm_result:  # If LLM succeeded
        return llm_result

    # Fallback heuristic
    import re
    sents = re.split(r'(?<=[.!?])\\s+', text.strip())
    sents = [s.strip() for s in sents if s.strip()]
    bullets = sents[:max_bullets]
    return "\n".join(f"- {b}" for b in bullets)

