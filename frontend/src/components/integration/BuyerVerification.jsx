import { useEffect, useState } from 'react'
import { checkoutApi } from '../../api/integrations'
import { Alert, Button, Field, Card } from '../ui'
export default function BuyerVerification({ token, onVerified }) {
  const [details, setDetails] = useState({ full_name: '', email: '', phone: '', address: '' })
  const [challenge, setChallenge] = useState(null)
  const [otp, setOtp] = useState('')
  const [wait, setWait] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => {
    if (!wait) return
    const timer = setTimeout(() => setWait(wait - 1), 1000)
    return () => clearTimeout(timer)
  }, [wait])
  const change = (key) => (event) => setDetails({ ...details, [key]: event.target.value })
  async function request(event) {
    event?.preventDefault(); if (busy) return
    setBusy(true); setError('')
    try { setChallenge(await checkoutApi(token, 'request-otp', details)); setOtp(''); setWait(60) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  async function verify(event) {
    event.preventDefault(); if (busy) return
    setBusy(true); setError('')
    try {
      const result = await checkoutApi(token, 'verify', { challenge_id: challenge.challenge_id, otp })
      await onVerified(result.session_token)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><h2 className="mb-4 text-lg font-semibold">{challenge ? 'Verify your email' : 'Buyer and delivery details'}</h2>
    <Alert>{error}</Alert>
    {!challenge ? <form onSubmit={request} className="mt-3 space-y-4">
      <Field label="Full name" required minLength={3} maxLength={120} value={details.full_name} onChange={change('full_name')} />
      <Field label="Email" required type="email" value={details.email} onChange={change('email')} />
      <Field label="Phone number" required minLength={7} maxLength={32} value={details.phone} onChange={change('phone')} />
      <Field label="Delivery address" required minLength={5} maxLength={500} value={details.address} onChange={change('address')} />
      <Button type="submit" disabled={busy}>Send verification OTP</Button>
    </form> : <>
      <p className="mb-3 text-sm text-slate-400">Enter the code emailed to {challenge.email}.</p>
      <form onSubmit={verify} className="space-y-4">
        <Field label="Email OTP" inputMode="numeric" pattern="[0-9]{6}" autoComplete="one-time-code" required maxLength={6} value={otp} onChange={(e) => setOtp(e.target.value)} />
        <Button type="submit" disabled={busy}>Verify and continue</Button>
      </form>
      <button type="button" disabled={busy || wait > 0} onClick={() => request()} className="mt-4 text-sm text-teal-300 disabled:text-slate-500">{wait ? `Send again in ${wait}s` : 'Send again'}</button>
    </>}
  </Card>
}
