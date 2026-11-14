import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Alert, Button, Card } from '../ui'
export default function LivePayment({ order, onPay, onRefresh }) {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function pay() {
    setBusy(true); setError('')
    try { setResult(await onPay({ method: 'mpesa', phone_number: order.verified_phone })) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><h2 className="text-lg font-semibold">Pay with M-PESA</h2>
    <p className="my-3 text-sm text-slate-400">This checkout requests a real M-PESA payment for the fixed bill above. Funds are held until you confirm receipt or your dispute is resolved.</p>
    <Alert>{error}</Alert>
    {order.verified_phone ? <><p className="my-3 text-sm text-slate-200">Your verified number: +{order.verified_phone}</p>
      <Button onClick={pay} disabled={busy || Boolean(result)}>{busy ? 'Requesting…' : 'Request M-PESA payment'}</Button></>
      : <p className="text-sm text-amber-200">Use an account with a phone verified by live SMS. <Link to="/login" className="underline">Sign in</Link>, open <Link to="/phone" className="underline">Phone & USSD</Link>, verify your number, then reopen this checkout and verify the same account email.</p>}
    {result && <p role="status" className="mt-4 text-sm text-teal-300">{result.message} {result.payment?.reference}</p>}
    <Button variant="ghost" className="mt-4" onClick={onRefresh} disabled={busy}>Refresh payment status</Button>
    <p className="mt-3 text-xs text-slate-500">Card charging is not available until a card provider is configured. A prompt or redirect is not proof of payment.</p>
  </Card>
}
