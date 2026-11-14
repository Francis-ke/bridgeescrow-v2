import { Link } from 'react-router-dom'
import { Alert, Button, Card, Field } from './ui'

export default function OtpPanel({ title, email, otp, setOtp, onSubmit, onResend,
  busy, error, submitLabel, children }) {
  return (
    <div className="mx-auto mt-16 max-w-md">
      <h1 className="mb-1 text-2xl font-bold">{title}</h1>
      <p className="mb-6 text-sm text-slate-400">
        We sent a 6-digit code to <span className="text-white">{email}</span>.
      </p>
      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <Alert>{error}</Alert>
          <Field label="Email OTP" value={otp} onChange={(e) => setOtp(e.target.value)}
            inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} placeholder="000000" required />
          {children}
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? 'Please wait…' : submitLabel}
          </Button>
        </form>
        <div className="mt-4 flex items-center justify-between text-sm">
          <button type="button" onClick={onResend} disabled={busy}
            className="text-teal-400 hover:text-teal-300">Send again</button>
          <Link className="text-slate-400 hover:text-white" to="/login">Go to sign in</Link>
        </div>
      </Card>
    </div>
  )
}
