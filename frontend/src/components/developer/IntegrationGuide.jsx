const additions = [
  ['A checkout button', 'Add “Pay with BridgeEscrow” beside your order total. Clicking it calls your own backend with the order reference. Your browser or mobile app must never contain your secret key.'],
  ['A backend checkout route', 'Your server loads the order from your database, validates the item prices and quantities, and calculates the KES bill. It creates an escrow, then a checkout session through the BridgeEscrow API. Do not trust a total sent by the browser.'],
  ['An order record', 'Save your shop order ID, the returned escrow ID, the checkout URL and the latest verified state together. Use a stable Idempotency-Key when creating the escrow so a network retry does not create a second order.'],
  ['A webhook receiver', 'Add a public HTTPS endpoint on your server and register its URL under your application’s webhooks. Verify each signature with your webhook secret, store event IDs to prevent duplicate processing, and update the matching order.'],
  ['An order status page', 'Show pending, funds held, released, disputed or refunded based on verified API responses or signed events. A checkout redirect alone is not proof of payment. Let customers return to their order and check its latest status.'],
]
const journey = [
  ['Buyer checks out on your website', 'Your checkout button sends the order reference to your server. The server uses its saved catalogue prices to prepare the bill.'],
  ['Your server creates protected checkout', 'Call POST /api/v1/escrows, save the returned escrow.id, then call POST /api/v1/checkout/sessions with that ID and method card or mpesa. Send the returned checkout_session.url to the browser and navigate the buyer there.'],
  ['BridgeEscrow hosts the payment steps', 'The buyer verifies their email, reviews the fixed bill and confirms the sandbox payment. Card and M-PESA flows are simulated; no real money moves.'],
  ['Your shop receives confirmation', 'Verify an escrow.held webhook or request GET /api/v1/escrows/{id}. HELD means the simulated funds are secured in escrow. Your order page can show “Funds held — preparing your order”.'],
  ['You fulfil the order and the buyer confirms', 'Deliver the goods or service. A release request asks for buyer authorization; it does not pay you automatically. Buyer confirmation releases the held funds. A dispute pauses release pending administrator resolution.'],
  ['Your order status stays in sync', 'Use escrow.released, escrow.disputed and escrow.refunded events, plus status requests when needed, to keep your records current. HELD and RELEASED represent different stages.'],
]
export default function IntegrationGuide({ liveEnabled = false }) {
  return <section aria-labelledby="integration-guide" className="space-y-6 rounded-2xl border border-white/10 bg-navy-800/60 p-5 sm:p-6">
    <div><h2 id="integration-guide" className="text-lg font-semibold">What to add to your website</h2>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">Keep your existing shop, catalogue and cart. Connect your checkout to BridgeEscrow through your server, and send the buyer to the hosted payment page. Creating an application here registers your integration; it does not install a checkout button on your website.</p></div>
    <div className="rounded-xl border border-teal-400/20 bg-teal-400/5 p-4"><h3 className="text-sm font-semibold text-teal-200">How payments are linked to you</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">Sign in to your own BridgeEscrow account, create an application, and generate its secret key. The connection is: your secret key → your application → your merchant account. When your website's server creates an order with that key, BridgeEscrow automatically records you as its seller. A website URL, public key or copied button alone does not establish this connection.</p>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">The buyer sees your application name as the seller at hosted checkout. Their email verification identifies the buyer separately. Your shop order ID links the payment back to the correct purchase in your database. Check the linked merchant account below before copying credentials.</p></div>
    <div className="grid gap-3 md:grid-cols-2">{additions.map(([title, text]) => <article key={title} className="rounded-xl border border-white/5 bg-navy-900/50 p-4">
      <h3 className="text-sm font-semibold text-teal-200">{title}</h3><p className="mt-2 text-sm leading-relaxed text-slate-400">{text}</p>
    </article>)}</div>
    <div className="rounded-xl border border-teal-400/15 p-4"><h3 className="text-sm font-semibold">Before you start</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">You need access to your website’s backend code, an order database and server environment variables. A static website needs a backend or serverless functions for the API calls and webhook receiver. Entering your Website URL here does not configure redirects or webhooks.</p>
      <p className="mt-2 text-sm leading-relaxed text-slate-400">Create a sandbox application below. Generate credentials with escrow:write, checkout:write and escrow:read for basic checkout. Add dispute:write or release:request only if you use those features. Save the API secret as BE_SECRET and the separate webhook signing secret as BE_WEBHOOK_SECRET on your server.</p></div>
    <div><h2 className="text-lg font-semibold">How a protected order works</h2>
      <ol className="mt-4 space-y-4">{journey.map(([title, text], index) => <li key={title} className="flex gap-3">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-teal-400/10 text-xs font-semibold text-teal-300">{index + 1}</span>
        <div><h3 className="text-sm font-medium text-slate-200">{title}</h3><p className="mt-1 text-sm leading-relaxed text-slate-400">{text}</p></div>
      </li>)}</ol></div>
    <p className="rounded-xl border border-amber-300/20 bg-amber-300/5 p-4 text-sm leading-relaxed text-amber-200">Test the full journey with sandbox credentials before planning a launch: held funds, failed payments, duplicate requests, buyer confirmation, disputes and webhook retries. {liveEnabled ? 'Production M-PESA is available only to verified accounts using separate live applications and keys. Card charging still requires a card provider.' : 'Production is disabled. Sandbox integrations cannot collect real payments or settle money to your business.'}</p>
  </section>
}
