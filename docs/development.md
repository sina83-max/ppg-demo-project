# Development Guide

## Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.11+ if running outside Docker

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

# Reset SQLite
rm merchant/merchant.db
```
