import { Link } from 'react-router-dom'
import { useState } from 'react'
import { protectedPayments as api } from '../../api/protected'
import { Button, Field, Alert } from '../ui'
export default function DisputeResolution({ dispute, onDone }) {
  const [outcome, setOutcome] = useState('resume')
  const [reason, setReason] = useState('')
  const [percent, setPercent] = useState(100)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('')
    try { await api.resolve(dispute.id, { outcome, resolution: reason, refund_percent: percent }); await onDone() }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <form onSubmit={submit} className="space-y-3 rounded-xl border border-white/10 p-4">
    <p className="text-xs uppercase text-teal-300">{dispute.category} · Escrow #{dispute.escrow_id}</p>
    {dispute.protected && <Link className="block text-sm text-teal-300" to={`/admin/payments/${dispute.escrow_id}`}>Review payment and work evidence →</Link>}
    <p className="text-sm">{dispute.reason}</p><Alert>{error}</Alert>
    <label className="block text-sm">Resolution
      <select value={outcome} onChange={(e) => setOutcome(e.target.value)} className="mt-1 w-full rounded-lg bg-navy-900 p-2">
        <option value="resume">{dispute.protected ? "Resume agreed workflow" : "Close dispute"}</option>{dispute.protected && <><option value="release">Release remaining funds</option>
        <option value="refund">Refund remaining funds</option><option value="split">Split remaining funds</option></>}
      </select>
    </label>
    {outcome === 'split' && <Field label="Refund to client (%)" type="number" min="0" max="100" required value={percent} onChange={(e) => setPercent(Number(e.target.value))} />}
    <Field label="Resolution reason" required minLength={10} maxLength={400} value={reason} onChange={(e) => setReason(e.target.value)} />
    <Button type="submit" disabled={busy}>{busy ? 'Resolving…' : 'Resolve dispute'}</Button>
  </form>
}
