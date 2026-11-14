export default function IntegrationGuide() {
  const example = JSON.stringify({ order_id: 'SHOP-1001', currency: 'KES', duration_hours: 72,
    items: [{ description: 'Package', quantity: 1, unit_amount: '300.00' }],
    return_url: 'https://your-shop.com/orders/SHOP-1001' }, null, 2)
  return <section className="space-y-4 text-sm">
    <h2 className="text-lg font-semibold">Connect your website</h2>
    <ol className="list-inside list-decimal space-y-3 text-slate-300">
      <li>Your server creates an order using the API key and the bill from your cart.</li>
      <li>Redirect the buyer’s “Pay with Escrow” button to the returned checkout_url.</li>
      <li>The buyer reviews the fixed total, verifies their email, and confirms payment.</li>
      <li>The buyer receives a delivery code by email. Ask for it only after delivery.</li>
    </ol>
    <p className="text-xs text-slate-400">POST /api/integrations/orders · Authorization: Bearer YOUR_SERVER_API_KEY</p>
    <pre className="overflow-x-auto rounded-xl bg-navy-900 p-4 text-xs text-teal-300">{example}</pre>
    <p className="text-xs text-slate-400">Poll GET /api/integrations/orders/ORDER_ID from your server for the payment state. Never trust a browser redirect as proof of payment.</p>
    <p className="text-xs text-slate-400">Release: POST /api/integrations/orders/ORDER_ID/redeem with {JSON.stringify({ code: 'BUYER_DELIVERY_CODE' })}. Keys can be revoked at any time.</p>
    <p className="text-xs text-amber-300">This workspace uses a test card processor. Live bank-card collection requires a payment-provider integration.</p>
  </section>
}
