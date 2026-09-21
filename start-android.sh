#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$(dirname "$0")"

MODEL_FILE="${MODEL_FILE:-qwen2.5-0.5b-instruct-q2_k.gguf}"
MODEL_PATH="$PWD/models/$MODEL_FILE"
LLAMA_SERVER="$PWD/llama.cpp/build/bin/llama-server"

if [ ! -x "$LLAMA_SERVER" ]; then
    echo "llama-server não encontrado."
    echo "Execute primeiro:"
    echo "bash install-android.sh"
    exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
    echo "Modelo não encontrado:"
    echo "$MODEL_PATH"
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "Ambiente Python não encontrado."
    echo "Execute bash install-android.sh"
    exit 1
fi

echo "Iniciando motor de IA..."
"$LLAMA_SERVER"     -m "$MODEL_PATH"     --host 127.0.0.1     --port 8080     -c 2048     -ngl 0     > llama.log 2>&1 &

LLAMA_PID=$!

cleanup() {
    echo
    echo "Encerrando Darck ChatGPT..."
    kill "$LLAMA_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

sleep 3

if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
    echo "O motor não iniciou."
    echo "Veja o log:"
    echo "cat llama.log"
    exit 1
fi

. .venv/bin/activate

export LLAMA_BASE_URL="http://127.0.0.1:8080"

echo
echo "======================================"
echo " DARCK CHATGPT V2"
echo "======================================"
echo "Interface: http://127.0.0.1:8000"
echo "Motor:     http://127.0.0.1:8080"
echo "======================================"
echo

python server.py
