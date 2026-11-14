import { useState } from 'react'
import { Alert, Button, Card, Field } from './ui'

export default function MpesaMethod({ onComplete }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event) {
    event.preventDefault(); if (busy) return; setError('')
    const data = new FormData(event.currentTarget)
    setBusy(true)
    try {
      await onComplete({ method: 'mpesa', amount: data.get('amount'), destination: data.get('destination') })
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return (
    <Card>
      <h2 className="mb-3 text-lg font-semibold text-teal-300">M-PESA</h2>
      <p className="mb-5 text-xs leading-relaxed text-slate-400">Enter the M-PESA phone number and amount.</p>
      <form onSubmit={submit} className="space-y-4">
        <Alert>{error}</Alert>
        <Field label="M-PESA phone number" name="destination"
          type="tel" inputMode="numeric" placeholder="254712345678" required />
        <Field label="Amount (KES)" name="amount" type="number" min="0.01" step="0.01" placeholder="0.00" required />
        <Button type="submit" disabled={busy} className="w-full">{busy ? 'Processing…' : 'Confirm transaction'}</Button>
      </form>
    </Card>
  )
}
