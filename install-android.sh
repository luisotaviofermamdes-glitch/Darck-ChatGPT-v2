#!/data/data/com.termux/files/usr/bin/bash
set -e

cd "$(dirname "$0")"

echo "== Darck ChatGPT v2 =="
echo "Instalando componentes..."

pkg update -y
pkg install -y git python clang cmake make wget

if [ ! -d "llama.cpp" ]; then
    echo "Baixando llama.cpp..."
    git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
fi

echo "Compilando llama.cpp..."
cmake -S llama.cpp -B llama.cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build llama.cpp/build -j2 --target llama-server

mkdir -p models data

if [ ! -f "models/qwen2.5-0.5b-instruct-q2_k.gguf" ]; then
    echo "Instalando ferramenta Hugging Face..."
    python -m pip install --upgrade pip huggingface_hub

    echo "Baixando modelo..."
    python -m huggingface_hub.commands.huggingface_cli download         Qwen/Qwen2.5-0.5B-Instruct-GGUF         qwen2.5-0.5b-instruct-q2_k.gguf         --local-dir models
fi

echo "Criando ambiente Python..."
python -m venv .venv

. .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo
echo "======================================"
echo " INSTALAÇÃO CONCLUÍDA"
echo "======================================"
echo
echo "Execute:"
echo "  bash start-android.sh"
echo
