import { useState } from 'react'
import { Button } from '../ui'
function Order({ order, busy, redeem }) {
  const [code, setCode] = useState('')
  return <li className="space-y-3 border-t border-white/10 py-4 text-sm">
    <div className="flex justify-between gap-3"><p className="font-semibold">{order.order_id}</p><p>KES {order.amount} · {order.state}</p></div>
    <a href={order.checkout_url} className="block break-all text-xs text-teal-300">{order.checkout_url}</a>
    {order.buyer && <div className="rounded-lg bg-navy-900 p-3 text-xs text-slate-300">
      <p>{order.buyer.name} · {order.buyer.email}</p><p>Deliver to: {order.buyer.shipping_name || order.buyer.name}</p><p>{order.buyer.phone}</p><p>{order.buyer.address}</p>
    </div>}
    {order.state === 'paid' && <form onSubmit={(event) => { event.preventDefault(); redeem(order.id, code) }} className="flex flex-wrap gap-2">
      <input aria-label={`Delivery code for ${order.order_id}`} required inputMode="numeric" pattern="[0-9]{8}" maxLength={8}
        value={code} onChange={(e) => setCode(e.target.value)} placeholder="Buyer’s delivery code" className="min-w-0 flex-1 rounded-lg border border-white/10 bg-navy-900 p-2" />
      <Button type="submit" disabled={busy}>Confirm delivery & release</Button>
    </form>}
  </li>
}
export default function SellerOrders({ orders, busy, redeem }) {
  return <section><h2 className="mb-4 text-lg font-semibold">Website orders</h2>
    {!orders.length && <p className="text-sm text-slate-400">No website orders yet.</p>}
    <ul>{orders.map((order) => <Order key={order.id} order={order} busy={busy} redeem={redeem} />)}</ul>
  </section>
}
