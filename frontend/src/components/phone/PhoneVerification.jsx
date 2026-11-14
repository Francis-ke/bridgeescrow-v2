import { useState } from 'react'
import { phoneApi } from '../../api/phone'
import { auth } from '../../api/endpoints'
import { useAuth } from '../../context/AuthContext'
import { Alert, Button, Card, Field } from '../ui'
export default function PhoneVerification({ onChange }) {
  const { user, updateUser } = useAuth()
  const [phone, setPhone] = useState(user?.phone_verified ? user.phone : '')
  const [challenge, setChallenge] = useState(null)
  const [otp, setOtp] = useState('')
  const [pin, setPin] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  async function run(task) {
    setBusy(true); setError(''); setMessage('')
    try { await task(); onChange() } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><h2 className="text-lg font-semibold">Link your phone</h2>
    <p className="my-3 text-sm text-slate-400">{user?.phone_verified ? `Verified: +${user.phone}. You can sign in with this number and your password.` : 'Verify a Kenyan mobile number to use phone login, USSD and SMS. Email login stays available.'}</p>
    <Alert>{error}</Alert>
    <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); run(async () => {
      setChallenge(await phoneApi.start(phone)); setOtp(''); setMessage('Code requested. In simulation mode, open your simulated SMS inbox below.')
    }) }}>
      <Field label="Phone number" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} required placeholder="0712345678" />
      <Button disabled={busy} type="submit">{challenge ? 'Send new verification code' : 'Send verification code'}</Button>
    </form>
    {challenge && <form className="mt-4 space-y-3" onSubmit={(e) => { e.preventDefault(); run(async () => {
      const data = await phoneApi.verify(challenge.challenge_id, otp); updateUser({ ...user, ...data.user })
      setChallenge(null); setOtp(''); setMessage('Phone verified. Use this number for login, SMS and USSD.')
    }) }}>
      <Field label="SMS verification code" value={otp} onChange={(e) => setOtp(e.target.value)} inputMode="numeric" pattern="[0-9]{6}" maxLength={6} required />
      <Button disabled={busy} type="submit">Verify phone</Button>
    </form>}
    <form className="mt-6 space-y-3 border-t border-white/10 pt-4" onSubmit={(e) => { e.preventDefault(); run(async () => {
      await auth.setPin(pin); setPin(''); setMessage('Transaction PIN saved. Use it when starting a USSD session.')
    }) }}>
      <Field label="Transaction PIN (4 digits)" type="password" inputMode="numeric" pattern="[0-9]{4}" maxLength={4} value={pin} onChange={(e) => setPin(e.target.value)} required />
      <Button disabled={busy} type="submit">Set transaction PIN</Button>
    </form>
    {message && <p role="status" className="mt-4 text-sm text-teal-300">{message}</p>}
  </Card>
}
