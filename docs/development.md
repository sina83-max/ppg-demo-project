# Development Guide

## Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.11+ if running outside Docker

## Running Outside Docker (local Python)

Each service is a standalone app whose package root is its own directory, so run
it **from that directory** — this is what makes `import app` resolve:

```bash
# one venv with both services' dependencies is fine
python -m venv .venv && . .venv/bin/activate
.venv/bin/pip install -r merchant/requirements.txt -r mock_ppg/requirements.txt

# terminal 1
cd merchant && DATABASE_URL=sqlite+aiosqlite:///./merchant.db \
  ../.venv/bin/uvicorn app.main:app --reload --port 8000

# terminal 2
cd mock_ppg && ../.venv/bin/uvicorn app.main:app --reload --port 8001
```

### IDE setup (PyCharm / IntelliJ)

Two settings are required, because `merchant/app` and `mock_ppg/app` are both
imported as the top-level package `app`:

1. **Interpreter** must have the dependencies installed:
   *Settings → Project → Python Interpreter*. If imports such as `fastapi` or
   `httpx` show as unresolved, the interpreter is a stale venv — install the two
   `requirements.txt` files into it.
2. **Source roots**: right-click `merchant` and `mock_ppg` →
   *Mark Directory as → Sources Root*. Without this, `from app.config import
   settings` cannot resolve, because the repository root is the content root and
   neither service directory is a Python package.

Alternatively, add the service directory to `PYTHONPATH`
(`PYTHONPATH=mock_ppg`).

## Quick Start (Mock mode)

```bash
cp .env.example .env
docker compose up --build
```

- Merchant dashboard: http://localhost:8000
- Mock PPG: http://localhost:8001

## Environment Variables

See `.env.example`.

Critical ones:

```env
# Merchant
PPG_BASE_URL=http://mock-ppg:8001
PPG_API_KEY=mock-key
PPG_SECRET_KEY=mock-secret
MERCHANT_CALLBACK_BASE=http://localhost:8000
DATABASE_URL=sqlite+aiosqlite:///./merchant.db

# Mock PPG
MOCK_PPG_PORT=8001
```

## Switching to Real Jibit PPG

1. Obtain real `apiKey` and `secretKey` from Jibit dashboard.
2. Update merchant environment:

```env
PPG_BASE_URL=https://napi.jibit.ir/ppg
PPG_API_KEY=your-real-key
PPG_SECRET_KEY=your-real-secret
```

3. Make sure your `callbackUrl` domain is whitelisted by Jibit.
4. Restart only the merchant service.

No code changes required.

## Running without Docker

```bash
# Terminal 1 – Mock
cd mock_ppg
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload

# Terminal 2 – Merchant
cd merchant
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload
```

## Project Conventions

- All PPG HTTP calls go through `app/clients/ppg_client.py`
- Business logic lives in `app/services/`
- Database access only in `app/repositories/`
- Routers stay thin

## Testing the Happy Path

1. Open http://localhost:8000
2. Create a purchase (amount ≥ 5000)
3. Click the switching URL (or the mock will auto-trigger callback)
4. Click **Verify**
5. Optionally click **Reverse**

## Useful Commands

```bash
# View logs
docker compose logs -f merchant
docker compose logs -f mock-ppg

# Reset SQLite (local runs)
rm merchant/merchant.db
rm mock_ppg/mock_ppg.db

# Reset SQLite (Docker: drops both volumes)
docker compose down -v
docker compose up --build
```

The mock's table is created on startup by `init_db()` and is never dropped
automatically, so a restart keeps the demo's purchases. Delete the file (or the
volume) to start clean.
