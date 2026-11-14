import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { auth } from '../api/endpoints'
import OtpPanel from '../components/OtpPanel'
import { Alert, Button, Card, Field } from '../components/ui'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [challenge, setChallenge] = useState(null)
  const [otp, setOtp] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  async function requestCode(e) {
    e.preventDefault(); setBusy(true); setError('')
    try { setChallenge(await auth.forgotPassword(email)) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function reset(e) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      if (password !== confirm) throw new Error('Passwords do not match')
      await auth.resetPassword({ email, otp, challenge_id: challenge.challenge_id,
        password, password_confirm: confirm })
      navigate('/login', { state: { message: 'Password updated. Sign in with your new password.' } })
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function resend() {
    setBusy(true); setError('')
    try { setChallenge(await auth.forgotPassword(email)); setOtp('') }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  if (challenge) return <OtpPanel title="Reset your password" email={challenge.email}
    otp={otp} setOtp={setOtp} onSubmit={reset} onResend={resend} busy={busy}
    error={error} submitLabel="Create new password">
    <Field label="New password" type="password" value={password}
      onChange={(e) => setPassword(e.target.value)} required />
    <Field label="Confirm new password" type="password" value={confirm}
      onChange={(e) => setConfirm(e.target.value)} required />
  </OtpPanel>

  return (
    <div className="mx-auto mt-16 max-w-md">
      <h1 className="mb-1 text-2xl font-bold">Forgot your password?</h1>
      <p className="mb-6 text-sm text-slate-400">Enter your email and we’ll send you an OTP.</p>
      <Card>
        <form onSubmit={requestCode} className="space-y-4">
          <Alert>{error}</Alert>
          <Field label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Sending code…' : 'Send OTP'}
          </Button>
        </form>
      </Card>
    </div>
  )
}
