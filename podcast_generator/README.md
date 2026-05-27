# 🎙️ PodcastAI — Gerador de Roteiros

Sistema de geração de roteiros e áudio para podcasts usando IA.

## Tecnologias

- **Backend**: Python + FastAPI
- **IA (roteiro)**: Claude (Anthropic API)
- **IA (áudio)**: gTTS (Google Text-to-Speech, PT-BR)
- **Frontend**: HTML/CSS/JS puro

## Estrutura

```
podcast_generator/
├── main.py              # Backend FastAPI
├── requirements.txt     # Dependências Python
├── static/
│   ├── index.html       # Frontend
│   └── audio/           # Áudios gerados (criado automaticamente)
└── README.md
```

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar a API Key da Anthropic

```bash
# Linux/Mac
export ANTHROPIC_API_KEY="sua-chave-aqui"

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sua-chave-aqui"
```

Obtenha sua chave em: https://console.anthropic.com

### 3. Rodar o servidor

```bash
cd podcast_generator
python main.py
```

O servidor inicia em: **http://localhost:8000**

## Como usar

1. Acesse `http://localhost:8000` no navegador
2. Digite o tema do seu episódio
3. Clique em **"Gerar roteiro"** — o Claude cria um roteiro completo
4. Clique em **"Gerar áudio do roteiro"** — o texto é narrado em PT-BR
5. Ouça o áudio direto no player ou baixe o MP3

## Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/` | Frontend web |
| POST | `/generate-script` | Gera roteiro via Claude |
| POST | `/generate-audio` | Converte texto em MP3 via gTTS |

### Exemplo de uso direto da API

```bash
# Gerar roteiro
curl -X POST http://localhost:8000/generate-script \
  -H "Content-Type: application/json" \
  -d '{"topic": "O futuro da energia solar no Brasil"}'

# Gerar áudio de um texto
curl -X POST http://localhost:8000/generate-audio \
  -H "Content-Type: application/json" \
  -d '{"topic": "Texto do roteiro aqui..."}'
```

## Observações

- Os arquivos de áudio ficam salvos em `static/audio/`
- Requer conexão com internet (Claude API + gTTS)
- Atalho: `Ctrl+Enter` na caixa de texto para gerar roteiro rapidamente
