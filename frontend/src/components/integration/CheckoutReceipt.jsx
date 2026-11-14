import { useState } from 'react'
import { checkoutApi } from '../../api/integrations'
import { Alert, Button, Card, Field } from '../ui'
export default function CheckoutReceipt({ order, token, session, onRefresh }) {
  const [sent, setSent] = useState(order.code_email_sent)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [completed, setCompleted] = useState(order.state === 'completed')
  const [disputed, setDisputed] = useState(false)
  const [reason, setReason] = useState('')
  async function resend() {
    setBusy(true); setError('')
    try {
      const result = await checkoutApi(token, 'delivery-code', {}, session)
      setSent(result.code_email_sent)
      if (!result.code_email_sent) setError('Email delivery failed. Please try again.')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  async function confirm() {
    setBusy(true); setError('')
    try {
      await checkoutApi(token, 'confirm', {}, session); setCompleted(true)
      await onRefresh?.(); window.dispatchEvent(new Event('account-updated'))
    }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  async function dispute(event) {
    event.preventDefault(); setBusy(true); setError('')
    try { await checkoutApi(token, 'dispute', { reason }, session); setDisputed(true); await onRefresh?.() }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card>
    <h2 className="text-xl font-semibold text-teal-300">{completed ? 'Delivery confirmed' : disputed || order.state === 'disputed' ? 'Payment disputed' : order.state === 'paid' ? 'Payment protected' : 'Order ' + order.state}</h2>
    <p className="mt-3 text-sm text-slate-300">Order {order.order_id} · KES {order.amount}</p>
    <Alert>{error}</Alert>
    {(disputed || order.state === 'disputed') && <p className="mt-4 text-sm text-amber-200">Funds remain protected while the dispute is reviewed.</p>}
    {order.state === 'paid' && !completed && !disputed && <>
      <p className="mt-4 text-sm text-slate-400">{sent ? 'Your unique delivery code was emailed to you.' : 'Your payment is secured, but the delivery code has not been emailed yet.'}</p>
      <p className="my-4 text-sm text-amber-300">Keep the code private. Give it to the seller only after receiving and checking your package. This releases the payment.</p>
      <Button disabled={busy} onClick={resend}>{busy ? 'Please wait…' : 'Send a new delivery code'}</Button>
      {['sandbox', 'production'].includes(order.environment) && <>
        <Button className="mt-3" disabled={busy} onClick={confirm}>{order.environment === 'production' ? 'Confirm receipt and release payment to seller' : 'Confirm completion and release sandbox funds'}</Button>
        <form onSubmit={dispute} className="mt-6 space-y-3 border-t border-slate-700 pt-5">
          <Field label="Dispute reason" required minLength={10} maxLength={400} value={reason} onChange={(event) => setReason(event.target.value)} />
          <Button type="submit" variant="ghost" disabled={busy}>Open a dispute</Button>
        </form>
      </>}
    </>}
    {order.return_url && <a href={order.return_url} className="mt-5 block text-sm text-teal-300">Return to shop →</a>}
  </Card>
}
