# Architecture

## Overview

This project consists of two FastAPI applications:

| Service     | Role                                      | Port (local) |
|-------------|-------------------------------------------|--------------|
| `merchant`  | Client application + Dashboard            | 8000         |
| `mock_ppg`  | Behavioral mock of Jibit PPG v3           | 8001         |

The merchant talks to PPG exclusively through `PPGClient`.  
By changing environment variables, the same merchant code can target either the local mock or the real Jibit API.

---

## Layered Architecture (Merchant)

```
┌─────────────────────────────────────────────┐
│                 API Layer                   │
│         (routers + Pydantic schemas)        │
└─────────────────────┬───────────────────────┘
                      │
┌─────────────────────▼───────────────────────┐
│               Service Layer                 │
│     (PurchaseService – business logic)      │
└─────────────┬─────────────────┬─────────────┘
              │                 │
┌─────────────▼──────┐   ┌──────▼──────────────┐
│  Repository Layer  │   │   Upstream Client   │
│ PurchaseRepository │   │     PPGClient       │
└─────────────┬──────┘   └─────────────────────┘
              │
┌─────────────▼──────┐
│   SQLite (aiosqlite)│
└────────────────────┘
```

### Responsibilities

**API Layer**
- Parse HTTP requests
- Validate input with Pydantic
- Call the appropriate service method
- Return HTTP responses / render templates
- No business rules

**Service Layer**
- Orchestrate use cases (create, handle callback, verify, reverse)
- Enforce domain rules (state transitions, uniqueness of `client_reference_number`, etc.)
- Call repository + PPGClient
- Map between domain objects and external DTOs

**Repository Layer**
- Pure data access
- SQLAlchemy queries only
- No knowledge of PPG or HTTP

**PPGClient**
- All HTTP communication with PPG (real or mock)
- Token lifecycle (generate + refresh)
- Translates PPG responses into plain dicts / simple objects

---

## Mock PPG Architecture

Kept intentionally simple:

- In-memory store (dict keyed by `purchase_id`)
- Minimal service layer
- Same endpoint paths and response shapes as real PPG
- No persistent database required

The mock exists only to enable realistic end-to-end demos and testing without credentials.

---

## Data Flow Examples

### Create Purchase

```
Browser → POST /purchases (merchant API)
       → PurchaseService.create_purchase()
           → PPGClient.create_purchase()          # calls mock or real
           → PurchaseRepository.create()          # save local copy
       → return purchase + switching URL
```

### Callback (from PPG / mock)

```
PPG/Mock → POST /callback (form-urlencoded)
        → PurchaseService.handle_callback()
            → update local purchase state
            → store raw payload
```

### Verify

```
Dashboard → POST /purchases/{id}/verify
         → PurchaseService.verify()
             → PPGClient.verify_purchase()
             → update local state from result
```

---

## Configuration

All configuration is loaded via `pydantic-settings` from environment variables / `.env`.

Critical settings:

| Variable              | Purpose                          | Example (mock)              |
|-----------------------|----------------------------------|-----------------------------|
| `PPG_BASE_URL`        | Target PPG                       | `http://mock-ppg:8001`      |
| `PPG_API_KEY`         | API key                          | `mock-key`                  |
| `PPG_SECRET_KEY`      | Secret key                       | `mock-secret`               |
| `MERCHANT_CALLBACK_BASE` | Base URL for callbacks        | `http://localhost:8000`     |
| `DATABASE_URL`        | SQLite connection                | `sqlite+aiosqlite:///./merchant.db` |

---

## Dashboard

- Server-side rendered with Jinja2
- Interactivity via Alpine.js (CDN, no build step)
- Pages:
  - Dashboard (list + actions)
  - Create purchase form
- No separate frontend project

---

## Deployment / Local Run

Docker Compose starts both services:

```yaml
services:
  mock-ppg:
    ...
  merchant:
    depends_on: [mock-ppg]
    environment:
      PPG_BASE_URL: http://mock-ppg:8001
```

For real PPG, the user only changes the environment variables of the `merchant` service.
