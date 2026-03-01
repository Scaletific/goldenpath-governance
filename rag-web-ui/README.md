# RAG Web UI

Standalone web interface for the GoldenPath Governance RAG pipeline.

See [PRD-0011](../docs/20-contracts/prds/PRD-0011-governance-rag-web-ui.md) and [ADR-0189](../docs/adrs/ADR-0189-rag-web-ui-tech-stack.md).

## Architecture

```
Browser → React SPA (Vite) → FastAPI → scripts/rag/* → ChromaDB + Neo4j
                                  ↓
                          AnswerContract JSON
                   (answer, evidence, limitations, next_step)
```

The FastAPI backend is a thin wrapper — all retrieval and synthesis is delegated to the existing `scripts/rag/` package.

## Quick Start (Local Development)

### Prerequisites

- Node.js 22+
- Python 3.12+
- ChromaDB running locally (container or native)
- Ollama running locally (for local LLM)

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python app.py        # http://localhost:8000
```

The Vite dev server proxies `/api/*` to the backend at `:8000`.

### Docker Compose

```bash
docker compose up    # Frontend :3000, Backend :8000, ChromaDB :8100
```

## Project Structure

```
rag-web-ui/
  frontend/
    src/
      components/       # React components (MessageBubble, EvidenceCard, etc.)
      lib/              # API client, types (AnswerContract mirror), utilities
      App.tsx           # Main chat interface
    index.html
    vite.config.ts      # Dev server + API proxy
    tailwind.config.ts
    package.json

  backend/
    app.py              # FastAPI routes: /ask, /health, /providers
    requirements.txt
    .env.example

  docker-compose.yml
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ask` | Question → AnswerContract JSON |
| GET | `/health` | Service health check |
| GET | `/providers` | Available LLM providers |

## Contract Enforcement

Every `/ask` response conforms to `schemas/metadata/answer_contract.schema.json`. Answers that fail validation are rejected (HTTP 500) — the UI never displays unsourced answers.
