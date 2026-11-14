import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { escrows } from '../api/endpoints'
import { Alert, Button } from './ui'

export default function HoldDecision({ escrow, onUpdate }) {
  const { user } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const request = escrow.transaction?.hold_request
  if (escrow.protection || user?.id !== escrow.transaction?.sender?.id || escrow.status !== 'funded'
      || request?.status !== 'pending') return null

  async function decide(decision) {
    setBusy(true); setError('')
    try {
      const result = await escrows.decideHold(escrow.id, decision)
      onUpdate?.(result.escrow)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <section className="mt-4 space-y-3 rounded-xl border border-teal-400/20 bg-teal-400/5 p-4">
      <h3 className="font-medium text-teal-300">Hold-time request</h3>
      <p className="text-sm text-slate-300">{escrow.seller} requested {request.hours} hours of hold time.</p>
      <p className="break-words text-sm text-slate-400">Reason: {request.reason}</p>
      <p className="text-xs leading-relaxed text-slate-500">
        Accept starts the requested hold from now. Decline keeps the existing hold unchanged.
        Neither option transfers or refunds money.
      </p>
      <Alert>{error}</Alert>
      <div className="flex gap-3">
        <Button disabled={busy} onClick={() => decide('accept')}>Accept</Button>
        <Button variant="ghost" disabled={busy} onClick={() => decide('decline')}>Decline</Button>
      </div>
    </section>
  )
}
