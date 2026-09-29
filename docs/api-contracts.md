# API Contracts

This document describes the contracts we implement and consume.

## 1. Real / Mock PPG Endpoints (we consume)

Base path: `/v3`

### Token

| Method | Path              | Auth | Body                          | Response          |
|--------|-------------------|------|-------------------------------|-------------------|
| POST   | `/tokens`         | No   | `{apiKey, secretKey}`         | `{accessToken, refreshToken}` |
| POST   | `/tokens/refresh` | No   | `{refreshToken}`              | `{accessToken, refreshToken}` |

### Purchase

| Method | Path                        | Auth | Body / Params                  | Response                  |
|--------|-----------------------------|------|--------------------------------|---------------------------|
| POST   | `/purchases`                | Yes  | `CreatePurchaseDto`            | `PurchaseCreationResult`  |
| GET    | `/purchases`                | Yes  | query filters                 | Paginated purchases       |
| POST   | `/purchases/{id}/verify`    | Yes  | none                           | `VerificationResultDto`   |
| POST   | `/purchases/reverse`        | Yes  | `{purchaseId? , clientReferenceNumber?}` | `ReverseResultDto` |

### Switching URL (special)

`GET /purchases/{purchaseId}/payments`  
In the real system this redirects the user to a PSP.  
In our mock it simulates payment success/failure and triggers the callback.

---

## 2. Merchant Public API (we expose)

These are the endpoints of **our** merchant application.

| Method | Path                          | Description                          |
|--------|-------------------------------|--------------------------------------|
| GET    | `/`                           | Dashboard (HTML)                     |
| GET    | `/purchases/new`              | Create purchase form (HTML)          |
| POST   | `/purchases`                  | Create purchase (form or JSON)       |
| POST   | `/callback`                   | PPG callback receiver (form-urlencoded) |
| POST   | `/purchases/{id}/verify`      | Trigger verify                       |
| POST   | `/purchases/{id}/reverse`     | Trigger reverse                      |
| GET    | `/api/purchases`              | JSON list of local purchases         |
| GET    | `/api/purchases/{id}`         | JSON single purchase                 |

---

## 3. CreatePurchaseDto (important fields)

Required by PPG:

```json
{
  "amount": 10000,
  "currency": "IRR",
  "callbackUrl": "https://...",
  "clientReferenceNumber": "unique-string"
}
```

Optional (supported by our client):

- `wage`
- `description`
- `userIdentifier`
- `payerMobileNumber`
- `payerNationalCode`
- `payerCardNumber` / `payerCardNumbers`
- `additionalData`
- `switching`

---

## 4. Callback Payload (form-urlencoded)

PPG (and our mock) will POST these fields to the merchant `callbackUrl`:

| Field                     | Present on success | Notes                          |
|---------------------------|--------------------|--------------------------------|
| `amount`                  | Yes                |                                |
| `wage`                    | Yes                |                                |
| `currency`                | Yes                | Always `IRR`                   |
| `purchaseId`              | Yes                |                                |
| `clientReferenceNumber`   | Yes                | URL-encoded                    |
| `status`                  | Yes                | `SUCCESSFUL` / `FAILED` / `UNKNOWN` |
| `payerIp`                 | Yes                |                                |
| `pspReferenceNumber`      | Success only       | URL-encoded                    |
| `pspRRN`                  | Success only       |                                |
| `payerMaskedCardNumber`   | Success only       |                                |
| `pspName`                 | Yes                | e.g. `saman-ipg`               |
| `pspTerminalId`           | Yes                |                                |
| `pspHashedCardNumber`     | Success only       |                                |
| `failReason`              | Failure only       |                                |

---

## 5. Error Format (from PPG)

```json
{
  "fingerprint": "uuid",
  "errors": [
    {
      "code": "purchase.invalid_state",
      "message": "..."
    }
  ]
}
```

Our `PPGClient` should surface the `code` clearly when raising exceptions.
