# BridgeEscrow V2 — Project Audit

## 1. Executive Summary

BridgeEscrow V2 is a full-stack escrow, direct transfer, and merchant payment platform designed for Kenya and East Africa. It provides:
- Core wallet functionality with double-entry accounting (available balance, escrow-held funds, incoming escrow).
- Protected Hold-Escro contracts across 11 category workflows.
- Direct wallet-to-wallet transfers (Send Money) using recipient account numbers, emails, or virtual cards.
- Safaricom Daraja M-Pesa integration (STK Push, B2C payouts, C2B simulation & live callbacks).
- Card payments (tokenized/hosted card checkout with no raw card storage).
- Developer & Merchant API with scoped API keys, webhooks, and hosted checkout sessions.
- USSD service and built-in USSD simulator with PIN protection and phone-account binding.
- Multi-channel notification pipeline (SMS, Email, and in-app feeds).
- Administrative control portal with dispute resolution, analytics, and merchant reviews.

---

## 2. Shared Account Bug — Root Cause Analysis & Permanent Fix

### Problem Observed
When multiple users logged into the platform or transferred money, balances, notification feeds, or transaction histories would occasionally leak or synchronize across accounts in client interfaces.

### Root Causes Identified
1. **Frontend Authentication Session Leakage**:
   - `AuthContext.jsx` stored `be_token` in `localStorage`, but did not register listeners for multi-tab `storage` events. When a user opened a second tab or switched accounts, token changes did not reset the in-memory state in the first tab.
   - When switching accounts, the previous profile was retained while the new profile request was in flight.
2. **Dashboard & Wallet State Race Conditions**:
   - `useWalletOverview` hook polled and fetched `/api/wallet` without associating the returned snapshot to the authenticated user's ID. In cases of network latency or concurrent tab switching, a late response from User A would overwrite User B's dashboard.
3. **HTTP Cache Control & Private Data Exposure**:
   - Authenticated API endpoints lacked `Cache-Control: private, no-store` headers and `Vary: Authorization`. Browsers and intermediate caches were allowed to cache responses across different authorization tokens.
4. **Global Idempotency Key Collisions**:
   - Previously, retry keys in wallet operations were checked globally across all users in `LedgerEntry`. If two accounts generated similar or default retry keys, transactions could be rejected or replayed into another wallet.
5. **Direct Transfer vs. Escrow Routing**:
   - The "Send Money" UI previously routed through demo escrows rather than atomic direct wallet transfers.

### Permanent Solution Implemented
1. **Frontend Session Synchronization**:
   - `AuthContext.jsx` now listens to `storage` events and immediately resets `user` to `null` and sets `loading: true` upon token changes or removals.
   - Profile restoration only commits if the active token still matches the token that initiated the request.
2. **Account-Isolated Dashboard Hook**:
   - `useWalletOverview(userId)` accepts the active `userId` and ignores responses if `value.user_id !== userId`.
   - `Dashboard.jsx` wraps the view in `<AccountDashboard key={user.id} user={user} />`, unmounting and resetting all component state when accounts change.
3. **Cache-Control Enforcement**:
   - An `after_request` handler in `backend/app/__init__.py` attaches `Cache-Control: private, no-store` and adds `Authorization` to the `Vary` header for all authenticated requests.
4. **Scoped Idempotency & Concurrency Locks**:
   - `backend/app/services/wallet_operations.py` implements `scoped_key(wallet, kind, key)` to hash and namespace retry keys to `w{wallet.id}-{kind}-{digest}`.
   - `lock(wallet)` executes `BEGIN IMMEDIATE` on SQLite and `SELECT ... FOR UPDATE` on MySQL to serialize concurrent balance mutations.
5. **Direct Wallet Transfer Service**:
   - `backend/app/services/direct_transfer.py` atomically debits the sender and credits the recipient within a single database transaction, recording distinct ledger entries and isolated notifications for each party.

---

## 3. Strict 79-Line File Architecture Compliance (Rule 1)

Every handwritten source file in the repository (.py, .js, .jsx, .ts, .tsx, .css, .html, .sql) is strictly less than 80 lines (maximum 79 lines).

- **Verification Tool**: `scripts/verify_lines.py` scans the repository and verifies line counts.
- **Automated Test**: `backend/tests/test_source_size.py` runs as part of `pytest` and fails if any file reaches 80 lines.
- **Modularity**: Large controllers and services are split into focused, single-responsibility modules (e.g., `auth_routes.py`, `auth_login.py`, `auth_otp.py`, `auth_pin.py`).

---

## 4. Security Audit Findings

| Category | Finding | Mitigation Status |
| :--- | :--- | :--- |
| **SQL Injection** | Parameterized queries via SQLAlchemy ORM throughout | PASS |
| **Authentication** | Passwords hashed with scrypt/Argon2; JWT tokens signed with secrets | PASS |
| **Session Isolation** | Multi-tab token synchronization, `no-store` headers, key scoping | PASS |
| **Card Data Safety** | No raw PANs or CVVs stored; tokenized/hosted card inputs only | PASS |
| **PIN Lockout** | 5 failed transaction PIN attempts locks account for 15 minutes | PASS |
| **Double Spending** | Database row locking and double-entry ledger reconciliation | PASS |
| **IDOR Protection** | Resource ownership strictly checked on escrows, wallets, and webhooks | PASS |
| **Webhook Integrity**| HMAC-SHA256 signature calculation and timestamp verification | PASS |
