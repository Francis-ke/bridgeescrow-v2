import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { escrows } from '../api/endpoints'
import { Alert, Button, Field } from './ui'

export default function ReceiptHoldForm({ escrow, onUpdate }) {
  const { user } = useAuth()
  const [duration, setDuration] = useState('1')
  const [unit, setUnit] = useState('days')
  const [reason, setReason] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  if (escrow.protection || user?.id !== escrow.transaction?.recipient?.id || escrow.status !== 'funded' || escrow.transaction?.hold_request?.status === 'pending') return null

  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setMessage('')
    try {
      const hours = Number(duration) * (unit === 'days' ? 24 : 1)
      if (!Number.isInteger(hours) || hours < 1 || hours > 720) {
        throw new Error('Choose between 1 hour and 30 days.')
      }
      const result = await escrows.receiptHold(escrow.id, { hours, reason: reason.trim() })
      onUpdate?.(result.escrow)
      setMessage('Request sent. Your sender must accept the requested hold time.')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <form onSubmit={submit} className="mt-5 space-y-3 border-t border-white/10 pt-4">
      <h3 className="font-medium text-white">Request hold time</h3>
      <p className="text-xs leading-relaxed text-slate-400">
        Choose how long funds should stay in escrow after the sender accepts. Your sender can accept or decline.
        An accepted hold does not automatically transfer money when it expires.
      </p>
      <Alert>{error}</Alert>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Hold duration" type="number" min="1" max={unit === 'days' ? 30 : 720}
          step="1" value={duration} onChange={(event) => setDuration(event.target.value)} required />
        <label className="block text-sm"><span className="mb-1 block text-slate-300">Time unit</span>
          <select value={unit} onChange={(event) => setUnit(event.target.value)}
            className="w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-white">
            <option value="hours">Hours</option><option value="days">Days</option>
          </select>
        </label>
      </div>
      <label className="block text-sm"><span className="mb-1 block text-slate-300">Reason for holding money</span>
        <textarea value={reason} onChange={(event) => setReason(event.target.value)} required
          minLength={10} maxLength={400} rows={3} placeholder="Explain why you need to hold this payment…"
          className="w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-white outline-none focus:border-teal-400" />
      </label>
      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : 'Send request'}</Button>
      {message && <p role="status" className="text-xs text-teal-300">{message}</p>}
    </form>
  )
}
