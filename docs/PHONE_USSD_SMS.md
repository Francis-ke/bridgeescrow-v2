# Phone, USSD, SMS and real M-PESA

## Where to paste credentials

For the local project, edit **backend/.env**. The labeled provider block contains empty fields for secrets. Do not put them in frontend environment variables, code examples, chat or source control. Restart the backend after changing this file.

For the supplied production containers, copy **deploy/production.env.example** to **deploy/production.env** and fill that private file instead. Production containers do not load your local backend/.env.

| Service | Configuration |
|---|---|
| Africa’s Talking SMS | `AT_USERNAME`, `AT_API_KEY`, optional approved `AT_SENDER_ID` |
| SMS mode | `SMS_MODE=simulated` for private local inbox; `africastalking` for provider requests |
| SMS environment | `AT_ENVIRONMENT=sandbox` for provider simulator; `live` for real SMS |
| USSD | `USSD_CALLBACK_TOKEN` (long random secret), provisioned `USSD_SERVICE_CODE`, `USSD_ENVIRONMENT=sandbox` or `live` |
| M-PESA collections | `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_SHORTCODE`, `MPESA_PASSKEY` |
| Payment mode | `PAYMENT_MODE=simulated`, `daraja_sandbox` or `daraja_live` |
| Collections callback | `MPESA_CALLBACK_URL=https://your-host/api/callbacks/mpesa` and `MPESA_CALLBACK_TOKEN` |
| B2C withdrawals | Approved `MPESA_B2C_INITIATOR`, `MPESA_B2C_SECURITY_CREDENTIAL`, result/timeout base URLs, then `MPESA_B2C_ENABLED=1` |
| Live merchant API | `DEVELOPER_LIVE_ENABLED=1` only with live Daraja, live verified phones and a clean database |

Generate each callback token using `python -c 'import secrets; print(secrets.token_urlsafe(32))'`. Do not reuse application keys or passwords as callback tokens. The server appends the payment reference and collection token to its configured callback URL. Configure USSD’s full callback as `https://your-host/api/ussd/gateway/YOUR_USSD_CALLBACK_TOKEN`. B2C result and timeout URLs use bases `https://your-host/api/payouts/result` and `/api/payouts/timeout`; the server appends the payout reference and callback token. Keep callback URLs out of access logs and restrict ingress to provider networks where supported.

## One phone across channels

Sign in with your existing email. Open **Phone & USSD**, request a phone verification code, and enter the SMS OTP. In local simulation mode, read it in your private simulated SMS inbox. Then set a four-digit transaction PIN. Email login stays available; phone login accepts the verified number plus the existing password. Kenyan local, 254 and +254 formats normalize to the same account. Simulated and provider-sandbox OTPs cannot establish live phone ownership.

A real phone number is not inferred from the legacy `WEB-...` account placeholder. Existing accounts must verify their number. A phone already held by another account cannot be claimed through this flow.

## USSD behavior

The real gateway accepts Africa’s Talking-style `sessionId`, `serviceCode`, `phoneNumber` and cumulative `text` form data. It returns plain `CON`/`END` responses. Every session requires the account’s transaction PIN. Sessions expire after three minutes and bind to one phone; five incorrect PIN attempts lock the PIN for fifteen minutes across sessions. Retried final callbacks return the cached result rather than sending another payment.

The menu supports balances, protected money transfers, legacy escrow release using an SMS code, escrow lists, protected-order lists, protected acceptance/funding/service confirmation/disputes, and M-PESA deposit requests. Complex order creation, milestones, extensions, merchant credentials and administrator actions remain on the website. This is shared account and business logic, not complete parity with every web screen.

The authenticated browser simulator uses `POST /api/ussd/simulate` with `{ "session_id": "a-new-random-session-id", "text": "" }`, then cumulative input such as `1234`, `1234*1`. It always uses the signed-in account’s verified phone. Never send a phone number to impersonate another user. Simulator transport does **not** make actions financially harmless: money operations use that account’s current wallet environment.

## SMS APIs and delivery

`GET /api/sms/messages` lists the signed-in user’s messages. Simulated bodies appear only to that user. Live message bodies, including OTPs, are not exposed by this API.

`POST /api/sms/simulate` creates a fixed BridgeEscrow test message for the signed-in user’s verified phone only in simulation mode. `POST /api/sms/test` requests a test message using the configured provider mode. It cannot send arbitrary messages or target other users. The simulate endpoint cannot send a real SMS and is disabled in provider mode. The test endpoint queues a provider request when configured. Bearer account authentication is required. These are BridgeEscrow messages, not forged Safaricom receipts.

Transaction notifications and release/delivery codes use the same SMS outbox for verified users. Run `flask --app wsgi deliver-sms --watch` continuously to deliver provider messages. Transient failures retry up to five attempts. `accepted` means accepted by the SMS provider, not confirmed handset delivery. A process crash during a provider request may leave `sending` uncertain; reconcile with the provider before resending. The system does not currently ingest handset delivery reports.

## Real payments and balances

The website selects a provider-aware Deposit/Withdraw screen when provider mode is enabled. Deposits use the account’s live-verified phone, accept whole KES, and require a stable idempotency key. A request or STK prompt never credits the wallet. The callback must match the stored CheckoutRequestID, amount, phone and receipt; a provider status query must also confirm success. Daraja sandbox confirmations never credit normal spendable balances.

Live merchant keys begin `be_live_sk_`; sandbox keys begin `be_test_sk_`. Application environments are immutable. Production checkout currently supports M-PESA, not cards. Buyers must verify their email and establish live SMS ownership of their phone on that same account. Verified provider payment creates the held escrow. Buyer receipt confirmation or the delivery code releases it to the seller’s Available Balance after fees. Seller incoming escrow is shown net of the reserved fee. Signed application webhooks track the same order lifecycle.

B2C payouts reserve wallet funds once. Confirmed failure refunds once; confirmed success does not debit a second time. An ambiguous transport failure or timeout stays `unknown` with funds reserved; it must be reconciled against the provider, not blindly refunded or retried with a new key. There is no automated B2C transaction-status reconciliation job yet. A live provider subscription and sufficient business B2C funds are required.

Do not turn existing test balances into real money. Live mode blocks databases containing simulated deposits or balances exceeding verified live collections after payouts. Use a separate, fresh production database. Keep this local database for testing.

## Production hosting

Set your domain’s DNS to the production server, allow ports 80/443, and fill `deploy/production.env`. Run `docker compose -f deploy/compose.yaml up --build -d`. The supplied configuration uses MySQL, Gunicorn, a static SPA server, Caddy HTTPS and continuously restarted SMS/webhook workers. Migrations run before the API starts. Only HTTPS entry points are public; database/API ports stay internal.

Run `flask --app wsgi channels-status` to inspect configuration without printing credentials, and `flask --app wsgi create-admin` interactively to create the first administrator. Schedule `bash deploy/backup-db.sh`, copy backups off the server, and verify restoration. The deployment files have not been launched against a public server in this local session. DNS, certificates, provider provisioning, delivery and real transactions require external validation.

## Provider references

- [Africa’s Talking USSD activation](https://help.africastalking.com/en/articles/9915125-how-do-i-go-live-with-ussd)
- [Africa’s Talking official Python SDK and SMS contract](https://github.com/AfricasTalkingLtd/africastalking-python)
- [Africa’s Talking sandbox limitations](https://help.africastalking.com/en/articles/1170660-how-do-i-get-started-on-the-africa-s-talking-sandbox)
- [Safaricom official SDK API payloads](https://github.com/safaricom/mpesa-php-sdk/blob/master/src/Mpesa.php)
