import { useState } from 'react'
import { Button } from '../ui'
export default function ReasonAction({ action, title, onAction, busy, extra = {} }) {
  const [reason, setReason] = useState('')
  async function submit(event) {
    event.preventDefault()
    if (await onAction(action, { ...extra, reason })) setReason('')
  }
  return <form onSubmit={submit} className="space-y-3 rounded-xl border border-white/10 p-4">
    <label className="block text-sm">{title}
      <textarea required minLength={10} maxLength={action === 'dispute' ? 400 : 10000} value={reason}
        onChange={(event) => setReason(event.target.value)} rows={2}
        className="mt-2 w-full rounded-lg border border-white/10 bg-navy-900 p-3" />
    </label>
    <Button type="submit" disabled={busy}>{title}</Button>
  </form>
}
