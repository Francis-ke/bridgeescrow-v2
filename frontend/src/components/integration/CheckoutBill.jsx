export default function CheckoutBill({ order }) {
  return <section className="rounded-2xl border border-white/10 bg-navy-800 p-5">
    <div className="flex flex-wrap items-center justify-between gap-3"><div>
      <p className="text-xs uppercase tracking-wider text-teal-300">Pay with Escrow</p>
      <h1 className="mt-1 text-xl font-semibold">{order.seller.name}</h1>
      <p className="mt-1 text-xs text-slate-500">Order {order.order_id}</p>
    </div><span className="rounded-full bg-amber-300/10 px-3 py-1 text-xs text-amber-300">{order.environment === 'production' ? 'Live M-PESA checkout' : order.environment === 'sandbox' ? 'Sandbox checkout' : 'Test checkout'}</span></div>
    <ul className="mt-5 divide-y divide-white/10">{order.items.map((item, i) => <li key={i} className="flex justify-between gap-4 py-3 text-sm">
      <span>{item.description} × {item.quantity}</span><span className="shrink-0">KES {(item.line_cents / 100).toFixed(2)}</span>
    </li>)}</ul>
    <div className="mt-3 flex justify-between border-t border-white/10 pt-4 font-semibold"><span>Total</span><span>KES {order.amount}</span></div>
    <p className="mt-2 text-xs text-slate-500">The shop supplies this bill. The total cannot be changed during checkout.</p>
  </section>
}
