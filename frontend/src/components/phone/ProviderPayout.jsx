import { useEffect, useRef, useState } from 'react'
import { get, post } from '../../api/client'
import { useAuth } from '../../context/AuthContext'
import { Alert, Button, Card, Field } from '../ui'
export default function ProviderPayout({ mode }) {
  const { user } = useAuth()
  const [amount, setAmount] = useState('')
  const [pin, setPin] = useState('')
  const [payout, setPayout] = useState(null)
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const key = useRef(crypto.randomUUID())
  async function refresh() {
    try { const data = await get('/payouts'); setRows(data.payouts); setPayout((current) => current ? data.payouts.find((row) => row.reference === current.reference) || current : null); window.dispatchEvent(new Event('account-updated')) }
    catch (err) { setError(err.message) }
  }
  useEffect(() => { refresh() }, [])
  useEffect(() => {
    if (!payout || ['succeeded', 'failed'].includes(payout.status)) return
    const timer = setInterval(refresh, 5000)
    window.addEventListener('focus', refresh)
    return () => { clearInterval(timer); window.removeEventListener('focus', refresh) }
  }, [payout?.id, payout?.reference, payout?.status])
  async function submit(event) {
    event.preventDefault(); if (busy) return; setBusy(true); setError('')
    try {
      const data = await post('/payouts', { amount, pin, idempotency_key: key.current })
      setPayout(data.payout); setPin(''); await refresh()
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><h1 className="text-xl font-semibold">Withdraw to M-PESA</h1>
    <p className="my-3 text-sm text-slate-400">Withdraw to your verified phone: {user?.phone_verified ? '+' + user.phone : 'verify your phone first'}. Approved B2C credentials are required. Funds are reserved while the provider processes the payout; a verified failure refunds them.</p>
    {mode !== 'daraja_live' && <p className="mb-3 text-sm text-amber-200">Payouts are disabled in provider sandbox mode.</p>}
    <Alert>{error}</Alert>
    <form className="space-y-3" onSubmit={submit}>
      <Field label="Withdrawal amount (whole KES)" type="number" min="10" max="150000" step="1" value={amount} onChange={(e) => setAmount(e.target.value)} required />
      <Field label="Transaction PIN" type="password" inputMode="numeric" pattern="[0-9]{4}" maxLength={4} value={pin} onChange={(e) => setPin(e.target.value)} required />
      <Button disabled={busy || Boolean(payout) || mode !== 'daraja_live' || !user?.phone_verified}>Request withdrawal</Button>
    </form>
    {payout && <p role="status" className="mt-4 text-sm text-teal-300">Payout {payout.reference}: {payout.status}. Pending or unknown payouts must be reconciled before retrying.</p>}
    {payout && ['succeeded', 'failed'].includes(payout.status) && <Button variant="ghost" onClick={() => { setPayout(null); key.current = crypto.randomUUID() }}>New withdrawal</Button>}
    <Button variant="ghost" onClick={refresh}>Refresh payouts</Button>
    <ul className="divide-y divide-white/10">{rows.map((row) => <li key={row.reference} className="py-3 text-xs text-slate-400">{row.reference} · KES {row.amount} · {row.status}</li>)}</ul>
  </Card>
}
