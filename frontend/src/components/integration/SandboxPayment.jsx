import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Alert, Button, Card, Field } from '../ui'
import CardEntry from '../CardEntry'
export default function SandboxPayment({ order, onPay, onFailure }) {
  const [params] = useSearchParams()
  const [method, setMethod] = useState(params.get('method') === 'mpesa' ? 'mpesa' : 'card')
  const [phone, setPhone] = useState(order.phone_number || '')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('')
    try { await onPay({ method: 'mpesa', phone_number: phone }) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  async function fail() {
    setBusy(true); setError('')
    try { await onFailure({ method }); setError('Test failure recorded. No funds were held. You can retry the checkout.') }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <section className="space-y-4">
    <p className="rounded-xl border border-amber-300/20 bg-amber-300/5 p-4 text-xs leading-relaxed text-amber-200">Sandbox checkout. Card and M-PESA payments are simulated. No live bank charge or M-PESA STK Push is sent, and normal account balances are not changed.</p>
    <div className="grid grid-cols-2 gap-2 rounded-xl bg-navy-800 p-1.5" aria-label="Sandbox payment method">{[['card', 'Card'], ['mpesa', 'M-PESA']].map(([value, label]) => <button key={value} type="button" aria-pressed={method === value}
      disabled={busy} onClick={() => { setMethod(value); setError('') }}
      className={`rounded-lg py-3 text-sm font-medium ${method === value ? 'bg-teal-400 text-navy-900' : 'text-slate-400'}`}>{label}</button>)}</div>
    <Alert>{error}</Alert>
    {method === 'card' ? <CardEntry kind="checkout" fixedAmount={order.amount} onComplete={(data) => onPay({ method: 'card', last4: data.last4 })} />
      : <Card><form onSubmit={submit} className="space-y-4">
        <Field label="M-PESA phone number" type="tel" inputMode="tel" required minLength={10} maxLength={20} value={phone} onChange={(event) => setPhone(event.target.value)} placeholder="254712345678" />
        <Field label="Amount (KES)" readOnly value={order.amount} />
        <Button type="submit" disabled={busy}>{busy ? 'Processing…' : 'Confirm sandbox M-PESA payment'}</Button>
      </form></Card>}
    <button type="button" disabled={busy} onClick={fail} className="text-xs text-slate-400 underline hover:text-amber-300">Simulate payment failure</button>
  </section>
}
