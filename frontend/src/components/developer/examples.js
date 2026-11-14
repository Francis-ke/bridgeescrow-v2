export function examples(base, environment = 'sandbox') {
  const bill = '{"order_id":"SHOP-1001","currency":"KES","items":[{"description":"Delivery package","quantity":1,"unit_amount":"300.00"}],"duration_hours":48}'
  const snippets = {
    cURL: `# Run on your server; never put BE_SECRET in browser code.
export BE_API="${base}/api/v1"
export BE_SECRET="your_saved_be_test_sk_key"
ORDER=$(curl -fsS -X POST "$BE_API/escrows" \\
  -H "Authorization: Bearer $BE_SECRET" \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: shop-1001-create" \\
  -d '${bill}')
ESCROW_ID=$(printf '%s' "$ORDER" | python3 -c 'import json,sys; print(json.load(sys.stdin)["escrow"]["id"])')
curl -fsS -X POST "$BE_API/checkout/sessions" \\
  -H "Authorization: Bearer $BE_SECRET" -H "Content-Type: application/json" \\
  -d "{\\"escrow_id\\":$ESCROW_ID,\\"method\\":\\"mpesa\\",\\"phone_number\\":\\"254712345678\\"}"
# Redirect your buyer to checkout_session.url.
curl -fsS "$BE_API/escrows/$ESCROW_ID" -H "Authorization: Bearer $BE_SECRET"`,
    Python: `import os
import requests
base = "${base}/api/v1"
headers = {"Authorization": "Bearer " + os.environ["BE_SECRET"]}
order = requests.post(base + "/escrows", headers={**headers,
    "Idempotency-Key": "shop-1001-create"}, timeout=15,
    json={"order_id": "SHOP-1001", "currency": "KES", "items": [
        {"description": "Delivery package", "quantity": 1, "unit_amount": "300.00"}]} )
order.raise_for_status()
escrow_id = order.json()["escrow"]["id"]
checkout = requests.post(base + "/checkout/sessions", headers=headers,
    json={"escrow_id": escrow_id, "method": "card"}, timeout=15)
checkout.raise_for_status()
print(checkout.json()["checkout_session"]["url"])
status = requests.get(base + "/escrows/" + str(escrow_id), headers=headers, timeout=15)
status.raise_for_status()
print(status.json()["escrow"]["state"])`,
    JavaScript: `// Node.js server code. BE_SECRET must not be bundled for a browser.
const base = "${base}/api/v1";
const headers = { Authorization: "Bearer " + process.env.BE_SECRET,
  "Content-Type": "application/json" };
async function call(path, options = {}) {
  const response = await fetch(base + path, { ...options,
    headers: { ...headers, ...options.headers } });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error?.message || "API request failed");
  return data;
}
const order = await call("/escrows", { method: "POST",
  headers: { "Idempotency-Key": "shop-1001-create" },
  body: JSON.stringify({ order_id: "SHOP-1001", currency: "KES", items: [
    { description: "Delivery package", quantity: 1, unit_amount: "300.00" }] }) });
const checkout = await call("/checkout/sessions", { method: "POST",
  body: JSON.stringify({ escrow_id: order.escrow.id, method: "card" }) });
// Redirect your customer from your backend to this hosted checkout URL:
console.log(checkout.checkout_session.url);
console.log(await call("/escrows/" + order.escrow.id));`,
  }
  return environment === 'production' ? Object.fromEntries(Object.entries(snippets).map(([key, value]) =>
    [key, value.replaceAll('be_test_sk_', 'be_live_sk_').replaceAll('"card"', '"mpesa"')])) : snippets
}
