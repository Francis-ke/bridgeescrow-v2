import { Button } from '../ui'
export default function WebhookDeliveries({ deliveries, busy, onRetry }) {
  return <section className="mt-4 border-t border-white/10 pt-4">
    <h3 className="mb-3 text-sm font-semibold">Delivery logs</h3>
    {!deliveries.length && <p className="text-xs text-slate-500">No deliveries yet. Send a sandbox test event to start.</p>}
    <ul className="space-y-3">{deliveries.map((delivery) => <li key={delivery.id} className="rounded-xl border border-white/10 bg-navy-900/40 p-3 text-xs">
      <div className="flex flex-wrap justify-between gap-2"><span className="font-mono text-teal-300">{delivery.event_type || delivery.type || 'Webhook event'}</span>
        <span className="text-slate-400">{delivery.status || delivery.state || 'queued'}</span></div>
      <p className="mt-2 break-all text-slate-500">Event {delivery.event_id || delivery.id}</p>
      <p className="mt-1 text-slate-400">Attempts: {delivery.attempts ?? delivery.attempt_count ?? 0} · HTTP {delivery.response_status || delivery.status_code || '—'}</p>
      {delivery.last_error && <p className="mt-2 break-words text-amber-300">{delivery.last_error}</p>}
      {['retry', 'failed'].includes(delivery.status) && (delivery.attempts ?? 0) < 5 && <Button variant="ghost" className="mt-3 text-xs" disabled={busy} onClick={() => onRetry(delivery.id)}>Retry delivery</Button>}
    </li>)}</ul>
  </section>
}
