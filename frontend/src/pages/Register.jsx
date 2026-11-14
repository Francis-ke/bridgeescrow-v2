import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { auth } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'
import OtpPanel from '../components/OtpPanel'
import { Alert, Button, Card, Field } from '../components/ui'

const EMPTY = { full_name: '', national_id: '', email: '', password: '', password_confirm: '' }

export default function Register() {
  const [form, setForm] = useState(EMPTY)
  const [challenge, setChallenge] = useState(null)
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { signIn } = useAuth()
  const navigate = useNavigate()
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      if (form.password !== form.password_confirm) throw new Error('Passwords do not match')
      setChallenge(await auth.register(form))
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function verify(e) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      const session = await auth.verifyRegistration({
        email: challenge.email, otp, challenge_id: challenge.challenge_id,
      })
      signIn(session); navigate('/')
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  async function resend() {
    setBusy(true); setError('')
    try { setChallenge(await auth.resendRegistration(challenge.email)); setOtp('') }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }

  if (challenge) return <OtpPanel title="Verify your email" email={challenge.email}
    otp={otp} setOtp={setOtp} onSubmit={verify} onResend={resend} busy={busy}
    error={error} submitLabel="Continue" />

  return (
    <div className="mx-auto mt-12 max-w-md">
      <h1 className="mb-1 text-2xl font-bold">Open a BridgeEscrow account</h1>
      <p className="mb-6 text-sm text-slate-400">Verify your email to activate your account.</p>
      <Card>
        <form onSubmit={submit} className="space-y-4">
          <Alert>{error}</Alert>
          <Field label="Full name" value={form.full_name} onChange={set('full_name')} required />
          <Field label="ID number" value={form.national_id} onChange={set('national_id')} required />
          <Field label="Email" type="email" value={form.email} onChange={set('email')} required />
          <Field label="Password" type="password" value={form.password} onChange={set('password')} required />
          <Field label="Confirm password" type="password" value={form.password_confirm}
            onChange={set('password_confirm')} required />
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Sending code…' : 'Create account'}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-400">
          Have an account? <Link className="text-teal-400" to="/login">Sign in</Link>
        </p>
      </Card>
    </div>
  )
}
