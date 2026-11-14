import { useState } from 'react'
import { Button, Field } from '../ui'
export const webhookEvents = ['payment.pending', 'payment.failed', 'escrow.held', 'escrow.released', 'escrow.disputed', 'escrow.refunded']
export default function WebhookForm({ initial, onSave, busy }) {
  const [url, setUrl] = useState(initial?.url || '')
  const [events, setEvents] = useState(initial?.events || webhookEvents)
  function submit(event) { event.preventDefault(); onSave({ url, events }) }
  return <form onSubmit={submit} className="space-y-4">
    <Field label="HTTPS webhook URL" type="url" pattern="https://.*" required placeholder="https://your-store.example/bridgeescrow/events" value={url} onChange={(event) => setUrl(event.target.value)} />
    <fieldset><legend className="mb-2 text-xs text-slate-400">Subscribed events</legend>
      <div className="grid gap-2 sm:grid-cols-2">{webhookEvents.map((item) => <label key={item} className="flex items-center gap-2 text-xs text-slate-300">
        <input type="checkbox" checked={events.includes(item)} className="accent-teal-400"
          onChange={(event) => setEvents(event.target.checked ? [...events, item] : events.filter((value) => value !== item))} />{item}
      </label>)}</div>
    </fieldset>
    <Button type="submit" disabled={busy || !events.length}>{initial ? 'Save webhook settings' : 'Register webhook'}</Button>
  </form>
}
