import { useState } from 'react'
import { payments } from '../api/endpoints'
import { Alert, Button, Card, Field } from './ui'

export default function DepositForm({ onDone }) {
  const [amount, setAmount] = useState('')
  const [msisdn, setMsisdn] = useState('')
  const [pending, setPending] = useState(null)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  async function startPayment(event) {
    event.preventDefault(); setBusy(true); setError(''); setMsg('')
    try {
      const result = await payments.stkPush(amount, msisdn)
      setPending(result.payment)
      setMsg('Deposit created. Confirm below to update your balance.')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function confirm() {
    setBusy(true); setError('')
    try {
      await payments.simulate(pending.id)
      setMsg('Deposit confirmed and wallet credited.')
      setPending(null); setAmount(''); onDone?.()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  return (
    <Card>
      <h1 className="text-xl font-bold">Deposit</h1>
      <p className="mb-5 mt-2 text-sm leading-relaxed text-slate-400">
        Enter the phone number and amount to deposit.
      </p>
      <Alert>{error}</Alert>
      {!pending ? <form onSubmit={startPayment} className="space-y-4">
        <Field label="Amount (KES)" type="number" min="1" step="0.01"
          value={amount} onChange={(event) => setAmount(event.target.value)} required />
        <Field label="M-PESA number" type="tel" inputMode="tel" value={msisdn}
          onChange={(event) => setMsisdn(event.target.value)} placeholder="254712345678" required />
        <Button type="submit" disabled={busy} className="w-full">
          {busy ? 'Creating…' : 'Create deposit'}
        </Button>
      </form> : <div className="space-y-3 text-sm">
        <p className="text-slate-300">KES {(pending.amount_cents / 100).toFixed(2)} · {pending.reference}</p>
        <Button disabled={busy} onClick={confirm} className="w-full">
          {busy ? 'Confirming…' : 'Confirm deposit'}
        </Button>
      </div>}
      {msg && <p role="status" className="mt-4 text-sm text-teal-300">{msg}</p>}
    </Card>
  )
}
