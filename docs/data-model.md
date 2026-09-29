# Data Model

## Purchase (Merchant local table)

We keep a local copy of every purchase so the dashboard works independently of PPG availability.

### SQLAlchemy Model (conceptual)

```python
class Purchase(Base):
    __tablename__ = "purchases"

    id: int                          # local primary key
    purchase_id: int | None          # ID returned by PPG
    purchase_id_str: str | None
    client_reference_number: str     # unique
    amount: int
    wage: int = 0
    currency: str = "IRR"
    state: str                       # see states below
    callback_url: str
    psp_switching_url: str | None
    description: str | None
    user_identifier: str | None

    # From callback / inquiry
    psp_name: str | None
    psp_reference_number: str | None
    psp_rrn: str | None
    payer_masked_card: str | None
    fail_reason: str | None
    raw_callback: str | None         # JSON or form data for debugging

    created_at: datetime
    updated_at: datetime
    verified_at: datetime | None
```

### States we track locally

```text
CREATED          # after we successfully called PPG create (before user pays)
IN_PROGRESS
READY_TO_VERIFY
SUCCESS
FAILED
EXPIRED
REVERSED
UNKNOWN
```

`CREATED` is a local convenience state.  
Once we receive a callback or do an inquiry we align with PPG states.

### Indexes / Constraints

- `client_reference_number` → unique
- Index on `purchase_id`
- Index on `state`

---

## Mock PPG Purchase Table

The mock keeps its purchases in its **own** SQLite file (ADR-008) – separate from
the merchant's, so either service can be reset without touching the other.

The purpose is fidelity, not persistence. SQLite makes two real-gateway
behaviors testable that a dict cannot reproduce:

- `client_reference_number` is **UNIQUE**, so the mock can reject a duplicate
  the way the real gateway does.
- `GET /v3/purchases` pages with real SQL `ORDER BY` / `LIMIT`.

### Model (conceptual)

```python
class Purchase(Base):
    __tablename__ = "purchases"

    id: int                          # surrogate key, never sent on the wire
    purchase_id: int                 # unique – the id the merchant calls back with
    client_reference_number: str     # unique – the merchant's own reference
    amount: int
    wage: int = 0
    currency: str = "IRR"
    state: str                       # see states below
    callback_url: str
    description: str | None
    user_identifier: str | None

    created_at: datetime             # naive UTC (SQLite drops tzinfo)
    updated_at: datetime
```

### Indexes / Constraints

- `purchase_id` → unique
- `client_reference_number` → unique
- Index on `state`

### Field naming

Columns are **snake_case**. The camelCase PPG payload (`purchaseId`,
`clientReferenceNumber`, …) is produced by `MockPurchaseService.to_wire()` –
the same DB/wire separation the merchant uses.

### Reset

```bash
rm mock_ppg/mock_ppg.db          # local run
docker compose down -v           # Docker: drops both volumes
```
