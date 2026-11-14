# Developer API interface

Sign in to BridgeEscrow and open **Developer API** in the hamburger menu. The page is integrated at `/developers/api`; the former `/seller/api` address redirects there. Existing website integrations, their keys and delivery-code redemption tools remain available through **Manage existing website integrations** at `/developers/api/legacy`.

1. Enter an application name, description, optional website and application type. The environment is sandbox.
2. Select an application from **My Applications** to edit its settings or deactivate it.
3. Choose server permissions and generate credentials. Copy the secret immediately; it is held only in page memory and is never stored in browser storage. Dismissing, revoking, switching applications or reloading removes the revealed secret. Public keys remain available. Rotation replaces the credential and reveals the new secret once.
4. Put the secret in your website backend's configuration. The embedded cURL, Python and Node.js examples create an immutable bill, start checkout and retrieve status using the implemented API endpoints.
5. Register a public HTTPS webhook receiver, select events and copy its signing secret once. The page includes raw-body HMAC verification instructions. Test events are queued; run `flask --app wsgi deliver-webhooks --limit 20` from the backend to deliver them. Delivery logs show attempts, response status and errors, with retry for eligible failures.

Hosted checkout verifies the buyer's email before accepting a sandbox card or M-PESA confirmation. The seller's bill and total remain visible and cannot be edited by the buyer. Raw card numbers and CVCs never leave the card-entry component; the sandbox receives only the selected method and last four digits. M-PESA uses the entered phone number. Neither method makes a bank charge or sends a live STK Push.

The **Simulate payment failure** button records a failed sandbox attempt while allowing a retry. After payment, the verified buyer can request a new delivery code, confirm completion to release sandbox funds, or open a dispute. The **Sandbox Environment** panel displays the application's isolated available, held and refunded amounts. For held orders, the application owner can enter the buyer's eight-digit delivery code to confirm delivery; the balance refreshes after release. Normal wallet balances are not used by the Developer API.

Frontend verification: run `npm test` and `npm run build` in `frontend/`. UI tests cover application management, secret handling and revocation, webhook registration and logs, navigation compatibility, fixed checkout totals, sandbox payment methods, failure, confirmation and disputes.
