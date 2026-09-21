# Darck ChatGPT V2 + Ollama

## 1. Instalar o Ollama
Instale o Ollama no computador/dispositivo compatível e deixe o serviço em execução.

## 2. Baixar um modelo
Exemplo:
ollama pull llama3.2:1b

Confira os modelos instalados:
ollama list

## 3. Iniciar o Darck ChatGPT V2

Linux/macOS:
AI_BACKEND=ollama DARCK_MODEL=llama3.2:1b bash start.sh

Windows PowerShell:
$env:AI_BACKEND="ollama"
$env:DARCK_MODEL="llama3.2:1b"
python server.py

Depois abra:
http://127.0.0.1:8000

## 4. Verificar a API
Abra:
http://127.0.0.1:8000/api/health

O backend deve mostrar "ok": true e "backend": "ollama".
