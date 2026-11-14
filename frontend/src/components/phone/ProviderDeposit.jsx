import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { phoneApi } from '../../api/phone'
import { payments } from '../../api/endpoints'
import { useAuth } from '../../context/AuthContext'
import { Alert, Button, Card, Field } from '../ui'
export default function ProviderDeposit({ mode }) {
  const { user } = useAuth()
  const [amount, setAmount] = useState('')
  const [payment, setPayment] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const key = useRef(crypto.randomUUID())
  useEffect(() => { payments.list().then((data) => {
    const pending = data.payments.find((row) => row.provider === mode && row.status === 'pending' && !row.checkout_order_id)
    if (pending) { setPayment(pending); setAmount(String(pending.amount_cents / 100)); setMessage('A previous payment request is still pending. Check its status before starting another.') }
  }).catch((err) => setError(err.message)) }, [mode])
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      const data = await phoneApi.deposit(amount, key.current)
      setPayment(data.payment); setMessage(data.message)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  async function refresh() {
    setBusy(true); setError('')
    try {
      const data = await payments.list()
      const latest = data.payments.find((item) => item.id === payment?.id)
      if (latest) setPayment(latest)
      window.dispatchEvent(new Event('account-updated'))
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><h1 className="text-xl font-semibold">M-PESA deposit</h1>
    <p className="my-3 text-sm text-slate-400">{mode === 'daraja_live' ? 'Live provider mode. Your wallet is credited only after verified payment confirmation.' : 'Daraja provider sandbox. Test confirmations do not credit spendable wallet funds.'}</p>
    <p className="my-3 text-sm text-slate-300">Phone: {user?.phone_verified ? '+' + user.phone : 'Not verified'}</p>
    <Alert>{error}</Alert>
    {!user?.phone_verified ? <Link className="text-sm text-teal-300 underline" to="/phone">Verify your phone first</Link> : <form className="space-y-4" onSubmit={submit}>
      <Field label="Amount (whole KES)" type="number" min="1" max="150000" step="1" value={amount} onChange={(e) => setAmount(e.target.value)} required readOnly={Boolean(payment)} />
      <Button disabled={busy || Boolean(payment)} type="submit">Request M-PESA payment</Button>
    </form>}
    {message && <p role="status" className="mt-4 text-sm text-teal-300">{message}</p>}
    {payment && <div className="mt-4 space-y-3 text-sm"><p>{payment.reference} · {payment.status}</p>
      <Button disabled={busy} variant="ghost" onClick={refresh}>Refresh payment status</Button>
      {['confirmed', 'failed'].includes(payment.status) && <Button variant="ghost" onClick={() => { setPayment(null); setMessage(''); key.current = crypto.randomUUID() }}>New deposit</Button>}
    </div>}
  </Card>
}
