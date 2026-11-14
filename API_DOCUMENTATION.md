# BridgeEscrow V2 — API Documentation

## Authentication & Headers
All authenticated endpoints require an `Authorization: Bearer <token>` header, except Merchant API endpoints which use `X-API-Key: <key>` or `Authorization: Bearer be_test_...`.

Responses return JSON. Rate limits and errors follow standard HTTP status codes:
- `200 OK` / `201 Created` / `202 Accepted`
- `400 Bad Request` / `401 Unauthorized` / `403 Forbidden` / `404 Not Found`
- `409 Conflict` (idempotency conflict or state violation)
- `422 Unprocessable Entity` (validation error)
- `429 Too Many Requests` (PIN lockout or rate limit)

---

## 1. Authentication Endpoints (`/api/auth`)

### `POST /api/auth/register`
Register a new customer account.
- **Request Body**:
  ```json
  {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "national_id": "12345678",
    "phone": "0712345678",
    "password": "Password123",
    "password_confirm": "Password123"
  }
  ```
- **Response**: `201 Created` with user snapshot.

### `POST /api/auth/login`
Sign in with email/phone and password.
- **Request Body**:
  ```json
  {
    "email": "jane@example.com",
    "password": "Password123"
  }
  ```
- **Response**: `200 OK` returning `{ "token": "...", "user": { ... }, "wallet": { ... } }`.

### `GET /api/auth/me`
Retrieve currently authenticated user profile and card details.

### `PUT /api/auth/me`
Update user profile full name.
- **Request Body**: `{ "full_name": "Jane Smith" }`

### `POST /api/auth/pin`
Set or update 4-digit transaction PIN.
- **Request Body**: `{ "pin": "1234" }`

---

## 2. Wallet & Financial Operations (`/api/wallet`)

### `GET /api/wallet`
Fetch user wallet balances: available, escrow, incoming_escrow, currency.
- **Response**:
  ```json
  {
    "wallet": {
      "user_id": 1,
      "available": "5000.00",
      "escrow": "0.00",
      "incoming_escrow": "0.00",
      "currency": "KES"
    }
  }
  ```

### `GET /api/wallet/ledger`
Retrieve audit history of all credits and debits for the current user's wallet.

### `POST /api/wallet/deposit`
Top up wallet funds (simulated or external payment).
- **Request Body**:
  ```json
  {
    "amount": "1000.00",
    "idempotency_key": "optional-uuid"
  }
  ```

### `POST /api/wallet/withdraw`
Withdraw funds from available wallet balance.
- **Request Body**:
  ```json
  {
    "amount": "500.00",
    "pin": "1234",
    "idempotency_key": "optional-uuid"
  }
  ```

### `POST /api/checkout/demo`
Execute direct transfer, simulated buy, or instant checkout.
- **Request Body (Direct Transfer)**:
  ```json
  {
    "kind": "send",
    "amount": 200.00,
    "destination": "recipient@example.com",
    "method": "card",
    "idempotency_key": "uuid"
  }
  ```

---

## 3. Protected Escrow Workflows (`/api/protected`)

### `GET /api/protected/categories`
List all 11 supported escrow categories and default rule sets.

### `POST /api/protected`
Create a category-specific escrow contract.
- **Request Body**:
  ```json
  {
    "category": "freelancing",
    "provider_id": 2,
    "title": "Website Design",
    "description": "Full responsive design implementation",
    "amount": "5000.00",
    "deadline": "2026-12-01T00:00:00Z",
    "rules": {
      "cancellation_deadline": "2026-11-20T00:00:00Z",
      "late_refund_percent": 80
    }
  }
  ```

### `POST /api/protected/:id/:action`
Perform an action on the escrow. Supported actions:
- `accept`: Second party accepts agreement terms.
- `fund`: Buyer funds contract from available wallet balance.
- `submit`: Provider submits completed work or milestone delivery.
- `revise`: Buyer requests milestone revisions.
- `approve`: Buyer approves submission and releases payment.
- `confirm`: Confirm booking / attendance.
- `cancel` / `decide-cancel`: Request or decide cancellation.
- `dispute`: Escalate contract to administrator dispute.

---

## 4. Developer & Merchant API (`/api/v1`)

### `POST /api/v1/escrows`
Create a merchant checkout escrow session.
- **Headers**: `Authorization: Bearer be_live_...` or `X-API-Key: ...`
- **Request Body**:
  ```json
  {
    "amount": "1500.00",
    "currency": "KES",
    "external_reference": "ORDER-991",
    "customer": { "email": "customer@example.com", "name": "Customer Name" },
    "redirect_url": "https://store.example/success"
  }
  ```

### `GET /api/v1/escrows/:id`
Check external escrow status (`PENDING`, `HELD`, `RELEASED`, `REFUNDED`).

### `POST /api/v1/escrows/:id/release-requests`
Merchant requests escrow release upon shipping/delivery.

### `POST /api/v1/escrows/:id/refunds`
Merchant issues full or partial customer refund.

---

## 5. Webhooks & Signatures
Events emitted: `payment.pending`, `escrow.held`, `escrow.released`, `escrow.refunded`, `dispute.opened`.

Payloads include:
- `X-BridgeEscrow-Signature`: `t=1700000000,v1=hex_hmac_sha256`
- Verification formula: `HMAC_SHA256(secret, t + "." + json_body)`
