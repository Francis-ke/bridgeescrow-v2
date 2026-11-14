# BridgeEscrow V2

Full-stack escrow platform: **Flask + MySQL + Python venv** API, **React 18 + Vite + Tailwind** SPA.
Every handwritten source file is **under 80 lines**.

## Requirements (Ubuntu 20.04+)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip mysql-server nodejs npm
```

Node **18+** is required by Vite 5 (check with `node -v`).

## 1. Database

```bash
sudo service mysql start
sudo mysql -e "CREATE DATABASE bridgeescrow_v2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'bridge'@'localhost' IDENTIFIED BY 'bridge';"
sudo mysql -e "GRANT ALL PRIVILEGES ON bridgeescrow_v2.* TO 'bridge'@'localhost'; FLUSH PRIVILEGES;"
```

## 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env          # edit DB credentials / secrets
flask --app wsgi db upgrade   # creates every table
python -m flask --app wsgi run --port 5050
```

Health check: `curl http://127.0.0.1:5050/api/health`

## 3. Frontend

```bash
cd frontend
npm install
npm run dev        # http://127.0.0.1:5180
```

Vite proxies `/api` to `http://127.0.0.1:5050`.

## 4. Tests

```bash
cd backend
python -m pytest tests -q     # isolated SQLite databases; mocked external services
```

Frontend checks:

```bash
cd frontend
npm test
npm run build
```

## Production containers

Copy `deploy/production.env.example` to `deploy/production.env` and configure
its database credentials, signing secrets, domain and provider settings. See
[deployment instructions](docs/PHONE_USSD_SMS.md) before enabling live payments.

```bash
docker compose -f deploy/compose.yaml up -d --build
```

## Main endpoints

- `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- `GET /api/dashboard`, `GET /api/wallet`, `GET /api/wallet/ledger`
- `POST /api/wallet/deposit`, `POST /api/wallet/withdraw`
- `GET|POST /api/escrows`, `POST /api/escrows/:id/fund|release|confirm|refund|cancel`
- `GET|PUT /api/escrows/:id/contract`, `POST /api/escrows/:id/contract/sign`
- `GET|POST /api/escrows/:id/disputes`
- `POST /api/payments/stk-push`, `POST /api/callbacks/mpesa`
- `GET /api/analytics/me`, `GET /api/admin/analytics`, `GET /api/admin/disputes`
- `POST /api/ussd` (Africa's Talking)

## Not yet built

Interactive analytics charts remain to be built. Merchant reports and the administrator
portal are available; live provider provisioning and delivery require external testing.

## Authentication email

Registration accepts only full name, ID number, email, password, and password
confirmation. Sign-in accepts email and password. Registration and password reset
send a six-digit email OTP; resend replaces the previous challenge. OTPs expire
in ten minutes and are never returned in API responses or printed to logs.

Email uses the sender configured by `MAIL_USERNAME` and `MAIL_FROM` in
`backend/.env`. OTPs go to each user's entered email address, never to a fixed
recipient. With Gmail, set `MAIL_PASSWORD` to the sender account's app password
and restart the backend. Template settings are in `backend/.env.example`;
editing that example does not change the running configuration. Do not commit credentials.
If delivery fails or the password is missing, the API returns an error instead
of reporting a successful send. A live delivery check requires this credential.
Tests use a captured test mailbox and mocked SMTP, without sending real email.

## Protected payment workflows

Buy goods and services now opens the Hold-Escro category selector. Freelancing
supports acceptance, deadlines, milestones, revisions, approval and disputes.
Booking supports provider reservations, secured funding, attendance/service
confirmation and booking-specific cancellation/refund rules. Both include
mutually agreed extensions, audit events, notifications and category reporting.
See [workflow setup and API details](docs/PROTECTED_PAYMENTS.md).

## Phone, USSD, SMS and provider payments

Open **Phone & USSD** to verify a phone, add phone/password login, set a transaction
PIN, use the shared-account USSD simulator, and inspect your private simulated SMS
inbox. Provider credential fields are labeled in `backend/.env` and `.env.example`.
Real services stay off until configured. See [setup, API contracts, live merchant
checkout, payouts and deployment](docs/PHONE_USSD_SMS.md). Production container
configuration is in `deploy/production.env.example`.
