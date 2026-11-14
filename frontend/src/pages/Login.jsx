import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { auth } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'
import { Alert, Button, Card, Field } from '../components/ui'
import OtpPanel from '../components/OtpPanel'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [byPhone, setByPhone] = useState(false)
  const [challenge, setChallenge] = useState(null)
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { signIn } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  async function submit(e) {
    e.preventDefault(); setBusy(true); setError('')
    try {
      signIn(await auth.login({ [byPhone ? 'phone' : 'email']: form.email, password: form.password }))
      navigate('/')
    } catch (err) {
      if (err.code === 'email_not_verified') {
        try { setChallenge(await auth.resendRegistration(form.email.trim())) }
        catch (sendError) { setError(sendError.message) }
      } else { setError(err.message) }
    } finally { setBusy(false) }
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
    otp={otp} setOtp={setOtp} onSubmit={verify} onResend={resend}
    busy={busy} error={error} submitLabel="Continue" />

  return (
    <div className="mx-auto mt-16 max-w-md">
      <h1 className="mb-1 text-2xl font-bold">Welcome back</h1>
      <p className="mb-6 text-sm text-slate-400">Sign in with your email or verified phone number and password.</p>
      <Card>
        <form onSubmit={submit} className="space-y-4">
          {location.state?.message && <p className="rounded-lg bg-teal-500/10 px-3 py-2 text-sm text-teal-300">
            {location.state.message}
          </p>}
          <Alert>{error}</Alert>
          <button type="button" className="text-sm text-teal-300" onClick={() => { setByPhone(!byPhone); setForm({ ...form, email: '' }) }}>{byPhone ? 'Use email' : 'Use phone number'}</button>
          <Field label={byPhone ? 'Phone number' : 'Email'} type={byPhone ? 'tel' : 'email'} value={form.email} onChange={set('email')} required />
          <Field label="Password" type="password" value={form.password} onChange={set('password')} required />
          <div className="text-right"><Link className="text-sm text-teal-400" to="/forgot-password">
            Forgot password?
          </Link></div>
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-400">
          New here? <Link className="text-teal-400" to="/register">Create an account</Link>
        </p>
      </Card>
    </div>
  )
}
