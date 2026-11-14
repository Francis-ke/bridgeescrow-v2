# BridgeEscrow V2 — Remaining Blockers & External Requirements

## Overview
All software components, business logic, multi-account isolation fixes, Hold-Escro workflows, USSD simulations, merchant endpoints, and automated tests are fully implemented and verified in this codebase.

To transition from the local/simulated environment to live real-money operations, the following external accounts, API credentials, and regulatory agreements must be obtained from external third parties.

---

## 1. Safaricom Daraja M-PESA Live Credentials

### Required for:
- Live STK Push deposits (`/api/payments/stk-push`).
- Live B2C payouts (`/api/payments/payout`).
- Live merchant settlements.

### External Actions Required:
1. Register a Daraja Live Developer Account on Safaricom's developer portal.
2. Obtain a live Paybill / Buy Goods Till number.
3. Apply for live B2C credentials (Initiator username, Security Credential certificate).
4. Deploy the application to a public HTTPS domain. Safaricom Daraja rejects non-HTTPS or localhost callback URLs.
5. Populate the following in `backend/.env`:
   - `PAYMENT_MODE=daraja_live`
   - `MPESA_CONSUMER_KEY`
   - `MPESA_CONSUMER_SECRET`
   - `MPESA_SHORTCODE`
   - `MPESA_PASSKEY`
   - `MPESA_CALLBACK_URL=https://your-domain/api/callbacks/mpesa`
   - `MPESA_B2C_INITIATOR`
   - `MPESA_B2C_SECURITY_CREDENTIAL`

---

## 2. Africa's Talking USSD & SMS Provider

### Required for:
- Real carrier USSD shortcode dialing (e.g. `*384*123#`).
- Real SMS OTP and transaction alerts.

### External Actions Required:
1. Register with Africa's Talking and obtain a dedicated or shared USSD Service Code from a telco carrier (Safaricom/Airtel).
2. Configure the USSD callback URL on Africa's Talking dashboard pointing to:
   `https://your-domain/api/ussd/gateway/<USSD_CALLBACK_TOKEN>`.
3. Obtain an approved Alphanumeric Sender ID for SMS delivery (requires telco letter of authorization in Kenya).
4. Configure in `backend/.env`:
   - `SMS_MODE=africastalking`
   - `AT_ENVIRONMENT=live`
   - `AT_USERNAME=your_at_username`
   - `AT_API_KEY=your_at_api_key`
   - `AT_SENDER_ID=your_sender_id`
   - `USSD_SERVICE_CODE=*384*...#`

---

## 3. Bank Card Acquirer / Payment Gateway

### Required for:
- Live Visa and Mastercard processing.

### External Actions Required:
1. Contract with a licensed Kenyan or East African payment service provider (e.g., Pesapal, DPO, Flutterwave, or bank merchant acquiring).
2. Integrate provider tokenization / hosted 3-D Secure checkout.
3. BridgeEscrow V2 does not store raw PANs or CVVs in adherence to PCI-DSS Level 1 compliance.

---

## 4. Production Mail Delivery (SMTP)

### Required for:
- Live customer email OTP delivery.

### External Actions Required:
1. Supply a production SMTP server (e.g. SendGrid, Amazon SES, or Gmail Workspace).
2. If using Gmail, generate a 16-character Google App Password (not account password).
3. Set `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_FROM` in `backend/.env`.

---

## 5. Regulatory & Financial Compliance

### Required for:
- Operating a multi-party escrow and custodial e-float service in Kenya.

### Actions Required:
1. Consult with the Central Bank of Kenya (CBK) regarding Payment Service Provider (PSP) licensing under the National Payment System Act.
2. Form partner-trustee arrangements with a licensed commercial bank to hold custodial customer funds in an escrow trustee account.
