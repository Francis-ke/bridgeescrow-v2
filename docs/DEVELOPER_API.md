# BridgeEscrow Developer API

> This document describes the sandbox API. Optional live M-PESA applications, separate live keys and provider setup are documented in [Phone, USSD, SMS and real M-PESA](PHONE_USSD_SMS.md). Live card charging is not configured.

The Developer API lets a registered, email-verified user create applications,
generate scoped sandbox credentials, create a protected checkout from a shop's
bill, and track payment and delivery. Open **Developer API** in the navigation
or visit `http://127.0.0.1:5180/developers/api` after signing in.

All new applications use **sandbox**. Card processing and M-PESA STK Push are
simulated: no bank charge, Safaricom prompt, or real transfer occurs. Production
financial operations are disabled. Existing seller integrations, stored keys,
orders, checkout links, wallets and protected-payment workflows remain available;
the developer page links to existing website integrations.

## Install, upgrade and run on Ubuntu

Use Python 3.10+ and Node 18+. This repository supplies `requirements.txt` and
`requirements-dev.txt`; it does not supply a Pipfile. A Python virtual environment
is supported directly:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm
cd /home/francis/Downloads/bridgeescrow-v2/backend
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

For an existing installation, keep `backend/.env` and its existing secrets.
Create a configuration file from the example only when one does not exist:

```bash
test -f .env || cp .env.example .env
```

The API reads `backend/.env`. Keep the existing `DATABASE_URL`, or configure
`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` and `DB_NAME` for MySQL. The URL
format is `mysql+pymysql://USER:ENCODED_PASSWORD@HOST:3306/DATABASE?charset=utf8mb4`.
Use a properly URL-encoded password. SQLite remains supported for local work and
automated tests. Do not switch an existing installation to an empty database.

Review these settings without replacing working credentials:

```dotenv
FLASK_RUN_PORT=5050
PUBLIC_FRONTEND_URL=http://127.0.0.1:5180
CORS_ORIGINS=http://localhost:5180,http://127.0.0.1:5180
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=YOUR_SENDER_ADDRESS
MAIL_FROM=YOUR_SENDER_ADDRESS
MAIL_PASSWORD=YOUR_SENDER_APP_PASSWORD
```

`MAIL_USERNAME` is the sender account. Checkout OTPs go to the buyer's entered
email address. Gmail requires an app password for that sender. Failed SMTP
delivery returns an error; it does not pretend to send an OTP. Restart the API
after changing configuration. Retain stable, private `SECRET_KEY` and
`JWT_SECRET` values: the former also encrypts stored webhook signing secrets.
Changing it without reissuing webhook secrets makes old secrets unreadable.

Back up the current database before migration. For MySQL, replace the uppercase
arguments with your configured account and database; `-p` prompts securely:

```bash
mysqldump --single-transaction -u DB_USER -p DB_NAME > bridgeescrow-before-20.sql
```

For SQLite, stop API/worker writes and use Python's SQLite backup API or `sqlite3
DATABASE_FILE '.backup BACKUP_FILE'`. Keep the backup outside the served files.
Then apply migrations using the existing configured database:

```bash
python -m flask --app wsgi db current
python -m flask --app wsgi db upgrade
python -m flask --app wsgi db current
python -m flask --app wsgi run --host 127.0.0.1 --port 5050
```

Revision **20**, following revision 19, adds developer applications, hashed
credentials, usage logs, rate windows, webhook endpoints/deliveries and nullable
developer linkage/idempotency fields on existing checkout orders. Existing
seller order data is preserved. Do not use `db.create_all()` as an upgrade or
delete a database to resolve a migration problem.

In another terminal:

```bash
cd /home/francis/Downloads/bridgeescrow-v2/frontend
npm install
npm run dev
```

The frontend runs at `http://127.0.0.1:5180`; Vite proxies `/api` to
`http://127.0.0.1:5050`. For a different API address, set `VITE_API_TARGET` in
`frontend/.env.local`, update `PUBLIC_FRONTEND_URL` and CORS origins as needed,
then restart both processes. Check `http://127.0.0.1:5050/api/health`.

Run the durable webhook worker in a third terminal with the same backend
environment and database:

```bash
cd /home/francis/Downloads/bridgeescrow-v2/backend
. .venv/bin/activate
flask --app wsgi deliver-webhooks --watch --interval 5
```

For a single worker pass, use `flask --app wsgi deliver-webhooks --limit 20`.
An endpoint test queues a real delivery; the worker must be running to send it.

## Applications, authentication and keys

Application management uses the user's ordinary login JWT:
`Authorization: Bearer USER_JWT`. The owner must be active and email verified.
Every application/key/webhook management lookup checks that owner's identity.
An application identifier in a management route can be its numeric `id` or
public `app_id` (`app_…`). Other owners receive 404.

Application creation accepts `name` (3–100 characters), `description` (10–2000),
`website` (optional HTTP/HTTPS URL), `type` (`website`, `mobile`, `backend`),
`environment` (`sandbox` only), and `active` (JSON boolean, default true).
PATCH accepts the same fields individually. Deactivating an application blocks
its keys and checkout funding, and cancels due webhook deliveries. Reactivating
an application does not restore revoked keys.

Each generated credential has a public key (`be_test_pk_…`) and a secret key
(`be_test_sk_…`). Only the secret can authorize external operations. The secret
is returned once on creation/rotation; only its SHA-256 hash and a short prefix
are stored. Lists never reveal it. Save it in the shop **server's** environment,
not React source, browser storage, query strings or public repository files.
Rotation creates a new secret and revokes the old credential atomically.

| Permission | Operation |
| --- | --- |
| `escrow:write` | Create a protected order |
| `escrow:read` | Read an application-owned order |
| `checkout:write` | Initiate its hosted checkout session |
| `dispute:write` | Open a dispute for its funded order |
| `release:request` | Ask the verified buyer to authorize release |

Key creation accepts a `name` and a nonempty `permissions` array. Omitting the
array grants all five scopes. Prefer only the scopes your server needs.

External requests use `Authorization: Bearer be_test_sk_…`. The persistent
limit is **60 requests per credential per UTC minute**, including authenticated
requests rejected for insufficient scope. A limit response is 429 with
`Retry-After`. Revoked, inactive, unknown, production or wrong-scope credentials
cannot perform financial operations. Public keys cannot authenticate.

All `/api/v1` responses include a generated `X-Request-ID`. Usage audit records
contain application/credential IDs when known, path, method, status, timestamp,
request ID and optional `Idempotency-Key` (up to 128 characters). They do not
store request/response bodies, authorization headers, raw API secrets, OTPs,
delivery codes, card numbers or CVCs. Failed requests are audited too. Audit
logging first rolls back unfinished route changes, so it cannot commit a failed
financial operation accidentally.

## REST endpoints

All request bodies are JSON. The paths below include their `/api` prefix.
“JWT” means the owner's login token; “key” means a scoped secret key.

| Method and path | Auth | Result |
| --- | --- | --- |
| `POST /api/auth/login` | Email/password | Login JWT in `token` |
| `GET /api/v1/developer/apps` | JWT | `{applications: [...]}` |
| `POST /api/v1/developer/apps` | JWT | `{application: {...}}`, 201 |
| `GET /api/v1/developer/apps/{app}` | JWT | Owned application |
| `PATCH /api/v1/developer/apps/{app}` | JWT | Edit or deactivate (`active: false`) |
| `GET /api/v1/developer/apps/{app}/keys` | JWT | `{credentials: [...]}` |
| `POST /api/v1/developer/apps/{app}/keys` | JWT | `{credential, secret_key}`, 201 |
| `DELETE /api/v1/developer/keys/{id}` | JWT | Revoke credential |
| `POST /api/v1/developer/keys/{id}/rotate` | JWT | New credential/one-time secret, 201 |
| `GET /api/v1/developer/apps/{app}/sandbox` | JWT | Isolated balances and latest 30 transactions |
| `POST /api/v1/escrows` | `escrow:write` key | Immutable order and checkout URL, 201 |
| `GET /api/v1/escrows/{id}` | `escrow:read` key | Current order state and verified buyer snapshot |
| `POST /api/v1/checkout/sessions` | `checkout:write` key | Hosted session URL, 201 |
| `POST /api/v1/escrows/{id}/disputes` | `dispute:write` key | Funded-order dispute, 201 |
| `POST /api/v1/escrows/{id}/release-requests` | `release:request` key | Await buyer confirmation, 202 |
| `GET /api/v1/developer/apps/{app}/webhooks` | JWT | `{webhooks: [...]}` |
| `POST /api/v1/developer/apps/{app}/webhooks` | JWT | Endpoint and one-time `signing_secret`, 201 |
| `PATCH /api/v1/developer/webhooks/{id}` | JWT | Edit URL/events or disable endpoint |
| `POST /api/v1/developer/webhooks/{id}/rotate-secret` | JWT | One-time replacement signing secret |
| `POST /api/v1/developer/webhooks/{id}/test` | JWT | Queue a test delivery, 202 |
| `GET /api/v1/developer/webhooks/{id}/deliveries` | JWT | Latest 100 delivery attempts/statuses |
| `POST /api/v1/developer/webhook-deliveries/{id}/retry` | JWT | Queue eligible retry without resetting attempt count |

No API key can look up another application's order, even if both applications
belong to the same user. The `id` used in `/api/v1/escrows/{id}` and checkout
session `escrow_id` is the numeric **API order ID**. The response's
`ledger_escrow_id` is a separate ledger escrow ID created only after funding.
Do not interchange them. `order_id` is your shop's original order reference.

Errors use `{error: {code, message, ...}}`; schema errors can include field
details. Typical statuses are 401 (authentication), 403 (scope/inactive), 404
(missing or other application's resource), 409 (state/idempotency conflict),
410 (expired checkout), 422 (validation), and 429 (rate limit).

## Build the immutable bill on your server

`POST /api/v1/escrows` accepts:

```json
{
  "order_id": "SHOP-1042",
  "currency": "KES",
  "duration_hours": 72,
  "return_url": "https://shop.example/orders/SHOP-1042",
  "items": [
    {"description": "Canvas bag", "quantity": 2, "unit_amount": "150.00"},
    {"description": "Delivery", "quantity": 1, "unit_amount": "50.00"}
  ]
}
```

The server calculates KES **350.00** from the line items. It accepts 1–50 items,
integer quantities 1–1000, unit amounts with at most two decimal places, and a
total from KES 10 to 5,000,000. Duration is 1–2160 hours; default 72. A developer
order reference is at most 80 characters. Currency is KES. Return URLs must be
HTTPS, or HTTP on `localhost`/`127.0.0.1` for local development.

Read prices from your trusted product/order database. Do not accept a browser's
claimed total or send it as a separate `amount` field. Buyers review the
server-calculated amount and item list in hosted checkout; they cannot edit the
bill there. Payment requests also do not accept a replacement amount.

The application plus `order_id` identifies one immutable bill. Retrying the
same normalized bill returns the same API order and stable checkout URL;
changing its items, duration, currency or return URL returns 409. An optional
`Idempotency-Key` header (1–128 characters) is additionally bound to that order
within the application. Reusing it for a different bill/order returns 409;
assigning a different nonempty key to an already-keyed order also conflicts.
Use the same reference, body and header after a network timeout. The audit
header alone is not a payment authorization. No duplicate funding or release
is performed by replaying a completed request.

Create a checkout session with `{"escrow_id": 123, "method": "card"}` or
`{"escrow_id": 123, "method": "mpesa", "phone_number": "0712345678"}`.
The session returns an opaque hosted URL. Redirect to that returned URL;
do not build an amount, secret key, OTP or buyer session into the redirect.
The public checkout link is an order locator, not authorization to fund or
release it. Pending checkout links expire after 24 hours.

## cURL: register the application and create a checkout

Start with a login JWT from an existing verified account. Keep shell secrets in
the current terminal, avoid committing generated output, and substitute your own
merchant details. Python is used only to extract JSON fields, so `jq` is not
required.

```bash
export BE_API_BASE=http://127.0.0.1:5050
read -r -s -p 'User JWT: ' BE_USER_JWT
export BE_USER_JWT
APP_RESPONSE=$(curl --fail-with-body -sS "$BE_API_BASE/api/v1/developer/apps" \
  -H "Authorization: Bearer $BE_USER_JWT" -H 'Content-Type: application/json' \
  -d '{"name":"Example Shop","description":"Protected checkout for our online shop","website":"https://shop.example","type":"website","environment":"sandbox"}')
export BE_APP_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["application"]["app_id"])' <<< "$APP_RESPONSE")
KEY_RESPONSE=$(curl --fail-with-body -sS "$BE_API_BASE/api/v1/developer/apps/$BE_APP_ID/keys" \
  -H "Authorization: Bearer $BE_USER_JWT" -H 'Content-Type: application/json' \
  -d '{"name":"Shop backend","permissions":["escrow:read","escrow:write","checkout:write","dispute:write","release:request"]}')
export BE_SECRET_KEY=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["secret_key"])' <<< "$KEY_RESPONSE")
unset KEY_RESPONSE

ORDER_RESPONSE=$(curl --fail-with-body -sS "$BE_API_BASE/api/v1/escrows" \
  -H "Authorization: Bearer $BE_SECRET_KEY" -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: shop-1042-checkout' \
  -d '{"order_id":"SHOP-1042","currency":"KES","duration_hours":72,"return_url":"https://shop.example/orders/SHOP-1042","items":[{"description":"Canvas bag","quantity":2,"unit_amount":"150.00"},{"description":"Delivery","quantity":1,"unit_amount":"50.00"}]}')
export BE_ESCROW_ID=$(python3 -c 'import json,sys; print(json.load(sys.stdin)["escrow"]["id"])' <<< "$ORDER_RESPONSE")
SESSION_RESPONSE=$(curl --fail-with-body -sS "$BE_API_BASE/api/v1/checkout/sessions" \
  -H "Authorization: Bearer $BE_SECRET_KEY" -H 'Content-Type: application/json' \
  -d "{\"escrow_id\":$BE_ESCROW_ID,\"method\":\"card\"}")
python3 -c 'import json,sys; print(json.load(sys.stdin)["checkout_session"]["url"])' <<< "$SESSION_RESPONSE"
```

Open the printed URL in the buyer's browser. After email verification and
payment, read status from your server:

```bash
curl --fail-with-body -sS "$BE_API_BASE/api/v1/escrows/$BE_ESCROW_ID" \
  -H "Authorization: Bearer $BE_SECRET_KEY"
```

After the service/delivery is ready, your server may request release:

```bash
curl --fail-with-body -sS "$BE_API_BASE/api/v1/escrows/$BE_ESCROW_ID/release-requests" \
  -H "Authorization: Bearer $BE_SECRET_KEY" -H 'Content-Type: application/json' \
  -d '{"reason":"The package has been delivered; please check it and confirm."}'
```

This returns `awaiting_buyer_confirmation` and leaves funds HELD. It sends the
buyer a notification. It does not transfer money by itself.

## Python standard-library server example

Run this on your shop backend with `BE_SECRET_KEY` in its environment. Replace
the sample line items with values loaded from your own database. The returned
URL is the value your HTTP endpoint should redirect the buyer to.

```python
import json
import os
from urllib.request import Request, urlopen

BASE = os.environ.get('BE_API_BASE', 'http://127.0.0.1:5050').rstrip('/')
SECRET = os.environ['BE_SECRET_KEY']

def api(path, body=None, idempotency_key=None):
    headers = {'Authorization': 'Bearer ' + SECRET, 'Content-Type': 'application/json'}
    if idempotency_key:
        headers['Idempotency-Key'] = idempotency_key
    data = None if body is None else json.dumps(body).encode()
    request = Request(BASE + path, data=data, headers=headers,
                      method='GET' if body is None else 'POST')
    with urlopen(request, timeout=15) as response:
        return json.load(response)

order = api('/api/v1/escrows', {
    'order_id': 'PY-SHOP-1042', 'currency': 'KES', 'duration_hours': 72,
    'return_url': 'https://shop.example/orders/PY-SHOP-1042',
    'items': [{'description': 'Canvas bag', 'quantity': 2, 'unit_amount': '150.00'}],
}, 'py-shop-1042-checkout')['escrow']
session = api('/api/v1/checkout/sessions', {
    'escrow_id': order['id'], 'method': 'card',
})['checkout_session']
print('Redirect buyer to:', session['url'])
print('Current state:', api('/api/v1/escrows/' + str(order['id']))['escrow']['state'])
# Once delivery is ready, a separate seller action can call:
# api(f"/api/v1/escrows/{order['id']}/release-requests", {'reason': 'Delivery ready'})
```

`urllib.error.HTTPError` contains the JSON error body for rejected requests.
Keep the original order reference and idempotency key when retrying.

## JavaScript server fetch example

This example is for a Node 18+ **server**, where `process.env.BE_SECRET_KEY`
stays private. Expose an authenticated shop endpoint that reads the customer's
cart from your database, calls this function, and returns an HTTP 303 redirect
to its result. The browser does not need the API secret.

```javascript
const base = (process.env.BE_API_BASE || 'http://127.0.0.1:5050').replace(/\/$/, '')
async function api(path, body, key) {
  const response = await fetch(base + path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { Authorization: `Bearer ${process.env.BE_SECRET_KEY}`,
      'Content-Type': 'application/json', ...(key ? { 'Idempotency-Key': key } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
    signal: AbortSignal.timeout(15000),
  })
  const result = await response.json()
  if (!response.ok) throw new Error(result.error?.message || `HTTP ${response.status}`)
  return result
}
async function createCheckout() {
  const { escrow } = await api('/api/v1/escrows', {
    order_id: 'JS-SHOP-1042', currency: 'KES', duration_hours: 72,
    return_url: 'https://shop.example/orders/JS-SHOP-1042',
    items: [{ description: 'Canvas bag', quantity: 2, unit_amount: '150.00' }],
  }, 'js-shop-1042-checkout')
  const { checkout_session } = await api('/api/v1/checkout/sessions', {
    escrow_id: escrow.id, method: 'mpesa', phone_number: '0712345678',
  })
  return { orderId: escrow.id, redirectUrl: checkout_session.url }
}
console.log(await createCheckout())
// Poll from the server when needed: await api(`/api/v1/escrows/${orderId}`)
// Request release separately; successful payment alone does not authorize release.
```

## Buyer verification, payment and release

Hosted checkout collects name, email, phone and delivery address, sends a real
six-digit email OTP, then enables payment after successful verification. OTPs
expire in ten minutes, allow at most five failed attempts and have a 60-second
resend cooldown. Verification produces a separate, hashed, 30-minute checkout
session. A public URL or seller API key cannot replace that buyer session.

The existing card-entry layout accepts the buyer's card details. In this
sandbox only the last four digits reach the API; raw PAN and CVC are not sent
or stored. M-PESA accepts a Kenyan phone number and simulates payment; no live
STK prompt is sent. “Simulate failed payment” creates a failed processor record
and event while leaving the checkout unpaid and retryable.

The server saves both parties' snapshots, verified buyer identity, shipping
details, calculated bill, timestamps, processor record and protected ledger
link. Sandbox funding, escrow hold, fees, release and refund use the existing
double-entry ledger and notification/admin dispute services. Inactive internal
accounts isolate each application's seller/fee wallets and each order's buyer
funds. Ordinary account balances and other applications' balances are unchanged.
The developer sandbox panel reports these isolated available/held/refunded
amounts. Released funds use the existing 1% provider fee calculation.

API states are `PENDING`, `HELD`, `RELEASED`, `DISPUTED`, `REFUNDED` and
`CANCELLED`. A failed processor attempt leaves the order `PENDING` so the buyer
can retry. A release request never bypasses buyer approval. The verified paying
buyer can confirm completion from the hosted receipt; repeat confirmation is
safe. A dispute blocks confirmation and seller release requests until an
administrator resolves it through the existing dispute portal. The order's
hold duration does not silently release disputed or unconfirmed funds.

The buyer also receives a private delivery code by email after funding. Existing
seller integrations retain their code-redemption workflow. Developer API
applications use the verified buyer's explicit confirmation; their API keys
cannot redeem a code or release funds directly. A buyer should only confirm
after receiving and checking the goods/service.

The hosted frontend uses these buyer-only routes; a verified session is passed
as `X-Checkout-Session` after OTP verification:

| Method and route | Purpose |
| --- | --- |
| `GET /api/checkout/{token}` | Public read-only bill; session adds buyer receipt details |
| `POST /api/checkout/{token}/request-otp` | Name/email/phone/address; send OTP |
| `POST /api/checkout/{token}/verify` | `challenge_id` + `otp`; return one-time session token |
| `POST /api/checkout/{token}/pay` | Verified buyer's `method`, `last4` or M-PESA phone |
| `POST /api/checkout/{token}/sandbox-failure` | Verified sandbox failure simulation |
| `POST /api/checkout/{token}/confirm` | Paying buyer authorizes protected release |
| `POST /api/checkout/{token}/dispute` | Paying buyer raises a dispute with `reason` |
| `POST /api/checkout/{token}/delivery-code` | Authorized buyer resends private delivery code |

Dispute reasons must contain at least ten characters. Seller release requests
and disputes accept `{"reason": "..."}` with at most 400 characters. Existing
admin dispute resolution remains responsible for release/refund outcomes.

## Signed webhooks

Create an endpoint under your application using the owner's JWT:

```json
{
  "url": "https://your-public-shop.example/webhooks/bridgeescrow",
  "events": ["payment.pending", "payment.failed", "escrow.held",
             "escrow.released", "escrow.disputed", "escrow.refunded"],
  "active": true
}
```

Save the returned `signing_secret` (`be_whsec_…`) once. It is encrypted at rest
and is never returned by list/detail endpoints. Rotating it immediately changes
the secret used for future delivery attempts. Keep `SECRET_KEY` stable and
coordinate receiver configuration before rotating.

| Event | Meaning |
| --- | --- |
| `payment.pending` | An immutable checkout has been created |
| `payment.failed` | A simulated processor attempt failed; retry is allowed |
| `escrow.held` | Funding succeeded and protected funds are held |
| `escrow.released` | Buyer-authorized release or admin release completed |
| `escrow.disputed` | A funded payment was disputed |
| `escrow.refunded` | Administrator dispute resolution refunded funds |

Payloads contain an envelope `id`, `type`, `created_at` and a `data` object with
API order ID, original order reference, environment, state, amount in cents and
currency. Payment events additionally contain `payment_state`. They do not
contain OTPs, checkout session tokens, private delivery codes, raw card details
or API secrets. The test button queues a `payment.pending` envelope whose data
contains `test: true`; treat it as a connectivity check.

Deliveries use these headers:

```text
BridgeEscrow-Signature: t=UNIX_SECONDS,v1=HEX_HMAC_SHA256
BridgeEscrow-Event-Id: EVENT_ID
Content-Type: application/json
```

The signed bytes are `timestamp + "." + exact_raw_request_body`, keyed with the
webhook signing secret using HMAC-SHA256. Verify the raw bytes before JSON
parsing, use constant-time comparison, reject timestamps more than five minutes
in the past or future, and deduplicate the envelope event ID. Never recreate
JSON to verify its signature. A minimal Python verifier is:

```python
import hashlib
import hmac
import json
import time

def verified_event(raw_body, signature_header, secret):
    fields = dict(part.split('=', 1) for part in signature_header.split(','))
    timestamp = fields['t']
    if abs(time.time() - int(timestamp)) > 300:
        raise ValueError('Expired webhook timestamp')
    expected = hmac.new(secret.encode(), timestamp.encode() + b'.' + raw_body,
                        hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, fields['v1']):
        raise ValueError('Invalid webhook signature')
    event = json.loads(raw_body)
    if not isinstance(event.get('id'), str):
        raise ValueError('Missing event ID')
    return event
```

Catch malformed headers/JSON as a 400 response. In the receiving shop database,
place a unique constraint on the processed event ID. In **one database
transaction**, insert that ID and apply the business update; on duplicate,
return 2xx without applying it again. Commit before acknowledging. A transient
failure should roll back both operations and return non-2xx. Do not mark an
event processed before its business update commits. Consider event order when
updating local order states; poll the scoped status endpoint if needed.

Only public HTTPS destinations are accepted. Creation and each send resolve
the host and reject private, loopback, link-local, reserved and mixed
public/private DNS results. The transport pins the validated IP, validates the
TLS hostname, enforces a ten-second deadline, and does not follow redirects.
A localhost listener is therefore unsuitable as an endpoint; use a reachable
HTTPS development endpoint. Application website/return URLs are separate from
these stricter outbound-webhook rules.

Any 2xx response marks delivery successful. Non-2xx, connection and TLS failures
retry after 60, 300, 900 and 3600 seconds, for **five total attempts**. A worker
claim has a 60-second lease so interrupted jobs can be recovered. Manual Retry
works only for `retry`/`failed` deliveries below the attempt limit and does not
reset it; delivered/in-flight/exhausted deliveries cannot be replayed that way.
Dashboard delivery details show status, attempts, last HTTP response, next
attempt and a sanitized error. Disabled endpoint/application jobs are cancelled.

## Architecture and verification

The new implementation is split into small modules; handwritten source files
remain below 80 lines.

| Area | Files |
| --- | --- |
| Developer UI | `frontend/src/pages/developer/`, `frontend/src/components/developer/`, `frontend/src/api/developer.js` |
| Hosted checkout | `frontend/src/pages/integration/HostedCheckout.jsx`, `frontend/src/components/integration/` |
| Application/key models | `backend/app/models/developer_application.py` |
| Audit/rate models | `backend/app/models/developer_usage.py` |
| Webhook models | `backend/app/models/webhook.py` |
| Schema upgrade | `backend/migrations/versions/20_developer_api.py`, `backend/migrations/helpers/developer_webhooks.py` |
| API routes | `backend/app/api/developer_apps.py`, `developer_escrows.py`, `developer_checkout.py`, `developer_buyer.py`, `developer_webhook_routes.py`, `developer_webhook_actions.py` |
| Services | `backend/app/services/developer/` for app/key auth, sandbox, lifecycle, delivery/signature/SSRF logic |
| Reused services | `integration_orders.py`, `checkout_*.py`, `protected/ledger.py`, notifications and administrator dispute resolution |
| Backend tests | `backend/tests/test_developer_*.py`, `test_webhook_*.py`, `test_mysql_workflow_schema.py` |
| Frontend tests | `frontend/src/pages/developer/*.test.jsx`, `frontend/src/pages/integration/*.test.jsx` |

Run the repository checks with isolated test data:

```bash
cd /home/francis/Downloads/bridgeescrow-v2/backend
. .venv/bin/activate
python -m pytest -q
cd ../frontend
npm test
npm run build
```

Backend tests default to in-memory SQLite and captured email rather than sending
real OTPs. Coverage includes ownership/scopes/revocation/rotation, persistent
rate limiting and audit rollback, immutable bills/idempotency, buyer email
verification, sandbox funding/release/refund isolation, balanced journal
entries, disputes, signatures/SSRF, retries and migration SQL compatibility.
The MySQL schema test compiles tables, indexes and locking statements with the
MySQL dialect; it does not by itself replace testing against a live MySQL
server. To run database tests against MySQL, use a separate disposable database
via `TEST_DATABASE_URL`; test fixtures recreate its tables. Never point it at
the application database.
