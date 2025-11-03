#!/usr/bin/env bash
set -euo pipefail
uvicorn agentic_research.server:app --host 0.0.0.0 --port 8000
