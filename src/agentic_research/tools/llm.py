from openai import OpenAI
from ..config import settings

client = None
if settings.OPENAI_API_KEY:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary_request(prompt: str) -> str:
    """
    Calls OpenAI to summarize text. 
    Gracefully fails if no key or error.
    """
    if client is None:
        return None  # signals fallback

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a research assistant. Summarize academic content into structured bullet points with methods, datasets, baselines, and contributions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return None  # fallback if OpenAI errors

