import { useState } from 'react'
import { Button, Field } from '../ui'
import { dateTime } from './format'
import { localDate } from './formValues'
export default function ExtensionControls({ payment, onAction, busy }) {
  const [deadline, setDeadline] = useState(localDate(192))
  const [reason, setReason] = useState('')
  async function submit(event) {
    event.preventDefault()
    await onAction('request-extension', { deadline: new Date(deadline).toISOString(), reason })
  }
  return <section className="space-y-3">
    {payment.extension && <p className="text-sm text-slate-400">Extension {payment.extension.status}: {dateTime(payment.extension.deadline)} · {payment.extension.reason}</p>}
    {payment.actions.includes('request-extension') && <form onSubmit={submit} className="space-y-3 rounded-xl border border-white/10 p-4">
      <Field label="Proposed completion deadline" type="datetime-local" required value={deadline} onChange={(e) => setDeadline(e.target.value)} />
      <Field label="Reason for extension" minLength={10} maxLength={10000} required value={reason} onChange={(e) => setReason(e.target.value)} />
      <Button type="submit" disabled={busy}>Request extension</Button>
    </form>}
    {payment.actions.includes('decide-extension') && <div className="flex gap-3">
      <Button disabled={busy} onClick={() => onAction('decide-extension', { decision: 'accept' })}>Accept extension</Button>
      <Button variant="ghost" disabled={busy} onClick={() => onAction('decide-extension', { decision: 'decline' })}>Decline extension</Button>
    </div>}
  </section>
}
