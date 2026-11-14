# Seller website checkout

Open **Seller API** on the BridgeEscrow dashboard (`/seller/api`). Enter the
business name, website and contact email, then create a key. The secret appears
once. Keep it on your shop's server; never put it in browser JavaScript. Keys
are stored as hashes and can be revoked from this page.

When hosting the application, set `PUBLIC_FRONTEND_URL` in `backend/.env` to
the public HTTPS frontend address and configure `CORS_ORIGINS` for that frontend.
Restart the API after configuration changes. External shops call your public
API origin; the default localhost address works only on your own computer.

The local application currently uses a **test card processor**. It records
protected payments in the existing double-entry ledger, but does not charge
bank cards. Connect a payment provider's hosted/tokenized card collection and
verified charge callbacks before accepting live card payments. No card number,
expiry or CVC is sent to or stored by this checkout API; only the last four
card digits are recorded. Email OTPs and delivery codes use the configured SMTP
sender, independently of the test processor.

## Create the bill on your server

Send `POST /api/integrations/orders` with
`Authorization: Bearer YOUR_SERVER_API_KEY` and `Content-Type: application/json`:

```json
{
  "order_id": "SHOP-1001",
  "currency": "KES",
  "duration_hours": 72,
  "items": [
    {"description": "Ordered package", "quantity": 1, "unit_amount": "300.00"}
  ],
  "return_url": "https://your-shop.com/orders/SHOP-1001"
}
```

Use the database cart prices on your server, rather than amounts received from
an untrusted browser. Each order supports 1–50 items, quantities 1–1,000 and
KES 10–5,000,000 in total. Use decimal strings with at most two decimal places.
The duration is 1–2,160 hours. Only KES is supported. The return URL must use
HTTPS; HTTP is permitted for localhost development.

The response contains `order.id` (BridgeEscrow's numeric ID), `order.order_id`
(your reference), the computed `amount`, `state` and `checkout_url`. Redirect
your **Pay with Escrow** button to that URL. The buyer sees the fixed bill and
cannot change the amount. Repeating the same reference and identical request
returns the original order; changing that reference's bill returns HTTP 409.
Unpaid checkout links expire after 24 hours.

## Buyer verification and payment

The hosted page collects buyer and delivery details, sends an email OTP, then
opens the card form after verification. OTPs expire after 10 minutes, allow
five incorrect attempts and can be resent after 60 seconds. Resending replaces
previous unused OTPs. Verification creates a guest account when needed; it does
not issue a general account login token. Guests can set a login password using
the normal forgotten-password process.

The verified checkout uses a random, hashed, order-specific session valid for
30 minutes. Payment retries are idempotent. Buyer and seller snapshots, the
order, protected payment, notifications and balanced ledger entries persist.
Only the verified buyer and owning seller can access buyer delivery details.

## Delivery and release

After payment the buyer receives a unique eight-digit delivery code by email.
Ask for it only after the buyer receives and checks the parcel. In Seller API,
enter it against the matching paid order, or have your server send:

```text
POST /api/integrations/orders/BRIDGEESCROW_NUMERIC_ID/redeem
Authorization: Bearer YOUR_SERVER_API_KEY
Content-Type: application/json

{"code":"01234567"}
```

Send the code as a string to preserve leading zeros. Five incorrect attempts
lock redemption until the verified buyer resends their delivery code. Resend
rotates the code and has a 60-second cooldown. Codes expire seven days after
the agreed delivery deadline. Successful redemption releases funds once, with
the existing 1% seller fee. Disputed or refunded payments cannot be redeemed.

If email delivery fails after payment, the payment remains secured and the
buyer can resend the code without paying twice. Neither the API response nor
the seller's dashboard exposes the buyer's code.

Poll `GET /api/integrations/orders/BRIDGEESCROW_NUMERIC_ID` from your server with
the same API key. States include `pending`, `paid`, `completed`, `disputed`,
`refunded` and `cancelled`. Only `paid` means the payment is secured; only
`completed` means released. Never treat the return URL or buyer browser as
proof of payment. Webhooks are not implemented; use authenticated polling.
