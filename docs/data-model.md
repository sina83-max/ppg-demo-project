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

## Mock PPG In-Memory Model

Simple dict is enough:

```python
{
  "purchase_id": int,
  "client_reference_number": str,
  "amount": int,
  "wage": int,
  "currency": "IRR",
  "state": str,
  "callback_url": str,
  "created_at": datetime,
  ...
}
```

No need for a real database in the mock.
