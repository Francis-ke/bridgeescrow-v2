const verification = `// Node.js webhook receiver: use the exact raw UTF-8 body, not reserialized JSON.
import { createHmac, timingSafeEqual } from "node:crypto";
function verifyWebhook(rawBody, signature) {
  const match = /^t=(\\d+),v1=([a-f0-9]{64})$/.exec(signature || "");
  if (!match) throw new Error("Invalid signature header");
  const [, timestamp, supplied] = match;
  if (Math.abs(Date.now() / 1000 - Number(timestamp)) > 300)
    throw new Error("Expired webhook timestamp");
  const expected = createHmac("sha256", process.env.BE_WEBHOOK_SECRET)
    .update(timestamp + ".").update(rawBody).digest();
  if (!timingSafeEqual(expected, Buffer.from(supplied, "hex")))
    throw new Error("Signature mismatch");
  const event = JSON.parse(rawBody.toString("utf8"));
  // Insert event.id into a UNIQUE database column before processing.
  // If already processed, acknowledge 2xx without applying it again.
  return event;
}`
export default function WebhookGuide() {
  return <details className="rounded-xl border border-white/10 p-4">
    <summary className="cursor-pointer text-sm font-medium text-teal-300">Webhook signatures, retries and error handling</summary>
    <div className="mt-4 space-y-4 text-xs leading-relaxed text-slate-400">
      <p>Verify the <code className="text-teal-200">BridgeEscrow-Signature</code> header using HMAC-SHA256 over the timestamp, a dot, and the exact raw request body. Envelopes contain id, type, created_at and data.</p>
      <pre className="overflow-x-auto rounded-xl bg-navy-900 p-4 text-[11px] text-slate-300"><code>{verification}</code></pre>
      <p>Return a 2xx status to acknowledge. Persist event IDs for duplicate protection. Failed deliveries are retried with delivery logs, up to five attempts. Use Retry delivery for eligible failed deliveries.</p>
      <p>For operators running this BridgeEscrow installation, dispatch queued events with: <code className="text-teal-200">flask --app wsgi deliver-webhooks --limit 20</code>. The merchant’s server only needs the HTTPS receiver. Public HTTPS receivers only; local/private addresses and unsafe redirects are blocked.</p>
      <p>Handle non-2xx API responses before using a returned ID. Errors use <code className="text-slate-200">{`{ "error": { "code": "…", "message": "…" } }`}</code>. Authentication/permission failures return 401/403, conflicting order retries return 409, invalid inputs return 422, and rate limits return 429. Do not blindly repeat financial requests: reuse the same order ID and idempotency key.</p>
    </div>
  </details>
}
