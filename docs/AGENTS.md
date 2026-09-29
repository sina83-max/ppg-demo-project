# AGENTS.md – Source of Truth for AI Coding Tools

This file is the **single source of truth** for any AI coding assistant (OpenCode, Cursor, Aider, Claude, etc.) working on this repository.

Read this file fully before making any changes.

---

## 1. Project Goal

Build a **demonstration merchant application** that integrates with Jibit PPG (Proxy Payment Gateway) v3.

The system has two parts:

1. **merchant** – A FastAPI application that acts as a payment client (the real product we care about).
2. **mock_ppg** – A lightweight FastAPI service that mimics the real Jibit PPG API so we can develop and demo without real credentials.

The merchant must work with **both**:
- Local `mock_ppg`
- Real Jibit PPG (`https://napi.jibit.ir/ppg`)

Switching between them must require **only environment variable changes**. No code changes.

---

## 2. Core Requirements

- Demonstrate the full purchase lifecycle: Create → Callback → Verify → Reverse
- Clean layered architecture (see below)
- Minimal but functional dashboard
- Easy to explain in a technical interview
- No over-engineering

---

## 3. Architecture (Mandatory)

We use a strict layered architecture:

```
API Layer (routers + schemas)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (data access)
    ↓
DB (SQLite)  +  Upstream Client (PPGClient)
```

### Rules

- Routers contain **no business logic**.
- Services contain **all business logic** and orchestration.
- Repositories only do CRUD / queries. No business rules.
- `PPGClient` is the **only** component that knows about HTTP calls to PPG (real or mock).
- The rest of the application never imports `httpx` for PPG calls.

---

## 4. Technology Stack (Do Not Change)

| Component       | Choice                          | Notes                                      |
|----------------|---------------------------------|--------------------------------------------|
| Language       | Python 3.11+                    |                                            |
| Web Framework  | FastAPI                         |                                            |
| DB             | SQLite via aiosqlite + SQLAlchemy 2.0 | Async                                    |
| Validation     | Pydantic v2                     |                                            |
| Settings       | pydantic-settings               |                                            |
| HTTP Client    | httpx (async)                   | Only inside `PPGClient`                    |
| Dashboard      | Jinja2 + Alpine.js              | No build step, no React/Vue/Svelte         |
| Container      | Docker + Docker Compose         |                                            |

**Forbidden**:
- React, Vue, Svelte, Next.js, or any SPA framework
- Celery / Redis / Kafka (out of scope)
- Complex event systems
- Microservices beyond the two apps (merchant + mock_ppg)

---

## 5. Directory Structure (Must Follow)

```text
ppg-demo/
├── docs/                          # This folder – source of truth
│   ├── AGENTS.md
│   ├── architecture.md
│   ├── api-contracts.md
│   ├── data-model.md
│   ├── flows.md
│   ├── decisions.md
│   └── development.md
├── merchant/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── dependencies.py
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   └── purchase_service.py
│   │   ├── repositories/
│   │   │   └── purchase_repository.py
│   │   ├── models/
│   │   │   └── purchase.py
│   │   ├── clients/
│   │   │   └── ppg_client.py
│   │   └── templates/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       └── create.html
│   ├── requirements.txt
│   └── Dockerfile
├── mock_ppg/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── dependencies.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── repositories/          # SQLAlchemy over SQLite (ADR-008)
│   │   ├── models/
│   │   └── ...
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 6. Key Domain Concepts

### Purchase States (must match real PPG)

```
IN_PROGRESS → READY_TO_VERIFY → SUCCESS
                              → FAILED
                              → EXPIRED
                              → REVERSED
                              → UNKNOWN
```

Also support `MANUALLY_SUCCESS` if needed for completeness.

### Important Fields

- `purchase_id` (from PPG)
- `client_reference_number` (unique per merchant)
- `amount`, `wage`, `currency` (IRR)
- `state`
- `psp_switching_url`
- `callback_url`
- Raw callback payload (for debugging)

---

## 7. PPG Client Contract

`merchant/app/clients/ppg_client.py` must expose:

```python
async def create_purchase(payload: dict) -> dict
async def verify_purchase(purchase_id: int) -> dict
async def reverse_purchase(purchase_id: int | None = None, client_reference_number: str | None = None) -> dict
async def get_purchase(purchase_id: int) -> dict
async def filter_purchases(**params) -> dict
```

It must handle:
- Token generation (`/v3/tokens`)
- Token refresh (`/v3/tokens/refresh`)
- Automatic token attachment (`Authorization: Bearer ...`)

Base URL and credentials come **only** from settings.

---

## 8. Mock PPG Behavior Rules

The mock must be behaviorally accurate enough for a realistic demo:

- Accept any `apiKey` / `secretKey`
- Return valid-looking tokens
- On create purchase → return `purchaseId` + `pspSwitchingUrl`
- Hitting the switching URL should:
  - Move purchase to `READY_TO_VERIFY`
  - POST form-urlencoded data to the merchant callback (same fields as real PPG)
- Verify only succeeds when state is `READY_TO_VERIFY`
- Reverse changes state to `REVERSED`
- Support returning `UNKNOWN` occasionally (for demo of retry logic)
- Persist purchases in its own SQLite file (ADR-008), so duplicate
  `clientReferenceNumber` is rejected and `GET /v3/purchases` can page with SQL

---

## 9. Dashboard Requirements

- Single page list of purchases + current state
- Button to create a new purchase
- Actions per purchase: Verify, Reverse, Refresh status
- Show callback data when available
- Use Alpine.js for interactivity (no complex state management)
- Server-rendered with Jinja2

---

## 10. Coding Guidelines for AI Agents

1. **Always read this file and `architecture.md` before editing.**
2. Prefer clarity over cleverness.
3. Keep functions small and focused.
4. Use type hints everywhere.
5. Do not add new dependencies unless absolutely necessary.
6. When adding a feature, update the relevant doc in `docs/` if behavior changes.
7. Never put business logic in routers.
8. Never put HTTP calls to PPG outside `ppg_client.py`.
9. Use async/await consistently.
10. Error responses from PPG should be propagated meaningfully (log + raise domain exceptions if needed).

---

## 11. Switching Between Mock and Real PPG

Only these environment variables change:

```env
# Mock
PPG_BASE_URL=http://mock-ppg:8001
PPG_API_KEY=mock-key
PPG_SECRET_KEY=mock-secret

# Real
PPG_BASE_URL=https://napi.jibit.ir/ppg
PPG_API_KEY=<real>
PPG_SECRET_KEY=<real>
```

---

## 12. Out of Scope (Do Not Implement)

- Real PSP payment pages
- Refund API
- Settlement API
- Multi-tenancy
- Authentication for the merchant dashboard
- Background workers / Celery
- Production-grade observability (basic logging is enough)

---

**End of AGENTS.md**
