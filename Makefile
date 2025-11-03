dev:
	uvicorn agentic_research.server:app --reload

test:
	pytest -q
