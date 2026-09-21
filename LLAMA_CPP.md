# Darck ChatGPT V2 + llama.cpp

O backend usa a API compatível com OpenAI fornecida pelo llama-server.

## Iniciar o llama-server

Exemplo:
llama-server -m ./models/seu-modelo.gguf --host 127.0.0.1 --port 8080

Depois inicie o Darck:
AI_BACKEND=llama DARCK_MODEL=local bash start.sh

Abra:
http://127.0.0.1:8000

## Verificar
http://127.0.0.1:8000/api/health

O servidor do llama.cpp deve estar acessível em:
http://127.0.0.1:8080
