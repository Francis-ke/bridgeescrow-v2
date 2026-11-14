import { useState } from 'react'
import { phoneApi } from '../../api/phone'
import { useAuth } from '../../context/AuthContext'
import { Alert, Button, Card, Field } from '../ui'
export default function UssdSimulator({ onChange, serviceCode }) {
  const { user } = useAuth()
  const [session, setSession] = useState(null)
  const [history, setHistory] = useState('')
  const [input, setInput] = useState('')
  const [reply, setReply] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const ended = reply.startsWith('END')
  async function dial(reset = false) {
    setBusy(true); setError('')
    const id = reset ? crypto.randomUUID() : session
    const text = reset ? '' : [history, input].filter(Boolean).join('*')
    try {
      const data = await phoneApi.dial(id, text)
      setSession(id); setHistory(text); setInput(''); setReply(data.reply)
      onChange(); window.dispatchEvent(new Event('account-updated'))
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><h2 className="text-lg font-semibold">USSD simulator</h2>
    <p className="my-3 text-sm leading-relaxed text-slate-400">Use the same account and wallet as the website. Verify your phone and set a transaction PIN first. This screen simulates the phone connection; actions affect your account.</p>
    <p className="mb-3 text-xs text-slate-500">{serviceCode ? `Configured provider code: ${serviceCode}. Carrier activation must be completed with your provider.` : 'No carrier code configured. A dialable USSD code must be provisioned by your provider.'}</p>
    <Alert>{error}</Alert>
    <Button disabled={busy || !user?.phone_verified} onClick={() => dial(true)}>{session ? 'Start new session' : 'Start session'}</Button>
    {reply && <pre role="status" className="my-4 whitespace-pre-wrap rounded-xl bg-navy-900 p-4 text-sm text-teal-200">{reply.replace(/^(CON|END)\s*/, '')}</pre>}
    {session && !ended && <form className="mt-3 space-y-3" onSubmit={(e) => { e.preventDefault(); dial() }}>
      <Field label="USSD response" type={history ? 'text' : 'password'} value={input} onChange={(e) => setInput(e.target.value)} autoComplete="off" required maxLength={160} />
      <Button type="submit" disabled={busy}>Send response</Button>
    </form>}
  </Card>
}
