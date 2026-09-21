#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
MODEL_PATH="$PWD/models/qwen2.5-0.5b-instruct-q2_k.gguf"
SERVER="$PWD/llama.cpp/build/bin/llama-server"
[ -x "$SERVER" ] || { echo "Execute primeiro: bash install-android.sh"; exit 1; }
[ -f "$MODEL_PATH" ] || { echo "Modelo não encontrado. Execute: bash install-android.sh"; exit 1; }
"$SERVER" -m "$MODEL_PATH" --host 127.0.0.1 --port 8080 -c 2048 -ngl 0 > llama.log 2>&1 &
LLAMA_PID=$!
trap 'kill $LLAMA_PID 2>/dev/null || true' EXIT
sleep 2
. .venv/bin/activate
python server.py
