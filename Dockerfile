# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

COPY ./src ./src
COPY .env.example ./.env

EXPOSE 8000
CMD ["uvicorn", "agentic_research.server:app", "--host", "0.0.0.0", "--port", "8000"]
