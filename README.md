# PPG Demo – Merchant + Mock Gateway

Demonstration project for integrating with **Jibit PPG (Proxy Payment Gateway) v3**.

This repository contains:

- **merchant** – FastAPI client application with a minimal dashboard
- **mock_ppg** – Behavioral mock of the real PPG API (no credentials needed)

The merchant works with **both** the local mock and the real Jibit API.  
Switching requires only environment variable changes.

---

## Documentation (Source of Truth)

All design decisions and contracts live in the `docs/` folder:

| File | Purpose |
|------|---------|
| [docs/AGENTS.md](docs/AGENTS.md) | **Main instructions for AI coding tools** |
| [docs/architecture.md](docs/architecture.md) | Layered architecture |
| [docs/api-contracts.md](docs/api-contracts.md) | Endpoints & payloads |
| [docs/data-model.md](docs/data-model.md) | Purchase model & states |
| [docs/flows.md](docs/flows.md) | Create → Callback → Verify → Reverse |
| [docs/decisions.md](docs/decisions.md) | ADRs |
| [docs/development.md](docs/development.md) | How to run & switch environments |

---

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

- Dashboard: http://localhost:8000
- Mock PPG:  http://localhost:8001

---

## Architecture Summary

```
API → Service → Repository → SQLite
                 ↘
                  PPGClient → (mock_ppg or real Jibit)
```

See `docs/architecture.md` for full details.

---

## Tech Stack

- FastAPI + Pydantic v2
- SQLAlchemy 2.0 + aiosqlite
- httpx
- Jinja2 + Alpine.js (dashboard)
- Docker Compose
