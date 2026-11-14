import { useState } from 'react'
import { Button } from '../ui'
import WebhookForm from './WebhookForm'
import WebhookDeliveries from './WebhookDeliveries'
export default function WebhookEndpoint({ webhook, busy, onUpdate, onRotate, onTest, onLogs, deliveries, onRetry }) {
  const [editing, setEditing] = useState(false)
  return <article className="rounded-xl border border-white/10 p-4">
    <div className="flex flex-wrap items-center justify-between gap-2"><p className="min-w-0 break-all text-sm text-slate-200">{webhook.url}</p>
      <span className={`text-xs ${webhook.active ? 'text-teal-300' : 'text-slate-500'}`}>{webhook.active ? 'Active' : 'Paused'}</span></div>
    <p className="mt-2 text-xs leading-relaxed text-slate-500">{webhook.events.join(' · ')}</p>
    <div className="mt-4 flex flex-wrap gap-2">
      <Button variant="ghost" disabled={busy} onClick={() => setEditing(!editing)}>{editing ? 'Close settings' : 'Configure'}</Button>
      <Button variant="ghost" disabled={busy} onClick={() => onUpdate(webhook.id, { active: !webhook.active })}>{webhook.active ? 'Pause' : 'Activate'}</Button>
      <Button variant="ghost" disabled={busy} onClick={() => onRotate(webhook.id)}>Rotate signing secret</Button>
      <Button variant="ghost" disabled={busy || !webhook.active} onClick={() => onTest(webhook.id)}>Send test event</Button>
      <Button variant="ghost" disabled={busy} onClick={() => onLogs(webhook.id)}>Delivery logs</Button>
    </div>
    {editing && <div className="mt-4"><WebhookForm initial={webhook} busy={busy} onSave={(body) => onUpdate(webhook.id, body)} /></div>}
    {deliveries && <WebhookDeliveries deliveries={deliveries} busy={busy} onRetry={onRetry} />}
  </article>
}
