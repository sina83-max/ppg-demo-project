# Core Flows

## 1. Create Purchase

```
Actor: Merchant user (via dashboard)
1. User fills amount + client_reference_number (+ optional fields)
2. Merchant API receives request
3. PurchaseService:
   a. Builds CreatePurchaseDto (adds callbackUrl automatically)
   b. Calls PPGClient.create_purchase()
   c. Saves local Purchase with state=CREATED / IN_PROGRESS
   d. Stores psp_switching_url
4. Dashboard shows the new purchase + link to switching URL
```

## 2. User Payment (Switching)

```
1. User opens psp_switching_url
2. In real PPG → redirects to actual PSP
3. In our mock:
   - Marks purchase as READY_TO_VERIFY
   - POSTs form-urlencoded callback to merchant /callback
   - Optionally shows a simple “Payment successful” page
```

## 3. Callback Handling

```
PPG/Mock → POST /callback (application/x-www-form-urlencoded)

PurchaseService.handle_callback():
1. Parse form fields
2. Find local purchase by purchaseId or clientReferenceNumber
3. Update state according to `status`:
   - SUCCESSFUL / UNKNOWN → READY_TO_VERIFY (or SUCCESS if auto-verify)
   - FAILED → FAILED
4. Store raw payload + PSP fields
5. Return 200 OK
```

## 4. Verify Purchase

```
1. User clicks “Verify” on dashboard (or auto after callback)
2. PurchaseService.verify(purchase_id):
   a. Call PPGClient.verify_purchase()
   b. Map result status:
      - SUCCESSFUL → local state = SUCCESS
      - FAILED → FAILED
      - UNKNOWN → UNKNOWN (can retry later)
      - ALREADY_VERIFIED → SUCCESS
      - NOT_VERIFIABLE → keep current / error
3. Update local record + verified_at
```

## 5. Reverse Purchase

```
1. User clicks “Reverse”
2. PurchaseService.reverse(purchase_id):
   a. Call PPGClient.reverse_purchase()
   b. On SUCCESSFUL → local state = REVERSED
   c. Handle ALREADY_REVERSED / NOT_REVERSIBLE / FAILED / UNKNOWN
```

## 6. Inquiry / Refresh Status

```
Dashboard “Refresh” button:
→ PPGClient.get_purchase() or filter
→ Update local state from PPG response
```

---

## State Transition Summary (Happy Path)

```
CREATED / IN_PROGRESS
        ↓ (user pays + callback)
READY_TO_VERIFY
        ↓ (verify)
SUCCESS
        ↓ (optional reverse)
REVERSED
```

Error / edge paths:

- No payment in time → EXPIRED
- Payment fails → FAILED
- Network issues on verify → UNKNOWN (retry)
