# Darck ChatGPT v2 — Android Local AI

IA local para Android/Termux com interface estilo ChatGPT.

## Recursos
- Interface mobile responsiva
- Modelo GGUF local via llama.cpp
- Streaming de respostas
- Histórico local
- Novo chat
- Apagar histórico
- Copiar respostas
- Markdown básico
- Seleção/configuração do modelo por variáveis de ambiente
- Sem API paga obrigatória

## Instalação rápida

No Termux:

    pkg update -y && pkg upgrade -y
    pkg install -y git
    git clone https://github.com/luisotaviofermamdes-glitch/Darck-ChatGPT-v2.git
    cd Darck-ChatGPT-v2
    bash install-android.sh

Depois:

    bash start-android.sh

Abra no navegador:

    http://127.0.0.1:8000

## Requisitos
Recomendado: Android 8+, Termux atualizado, pelo menos 2 GB livres e mais espaço para modelos maiores.

O instalador compila llama.cpp localmente. A compilação pode levar algum tempo.

## Modelo
Por padrão, o instalador baixa:
Qwen2.5-0.5B-Instruct-GGUF Q2_K.

Para trocar o modelo, coloque outro GGUF em models/ e altere MODEL_FILE no start-android.sh.

## Comandos úteis

Parar:
    Ctrl+C

Iniciar novamente:
    cd ~/Darck-ChatGPT-v2
    bash start-android.sh

Ver log do motor:
    cat llama.log

## Arquitetura

Android -> navegador -> FastAPI -> llama.cpp -> modelo GGUF

Tudo é executado localmente depois que os arquivos/modelo já foram baixados.
