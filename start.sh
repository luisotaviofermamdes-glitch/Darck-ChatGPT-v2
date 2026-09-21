#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install -r requirements.txt

export AI_BACKEND="${AI_BACKEND:-llama}"
export LLAMA_BASE_URL="${LLAMA_BASE_URL:-http://127.0.0.1:8080}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
export DARCK_MODEL="${DARCK_MODEL:-local}"

python server.py
