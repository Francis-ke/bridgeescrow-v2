import { useEffect, useState } from 'react'
import { phoneApi } from '../../api/phone'
import { Alert, Button, Card } from '../ui'
export default function SmsInbox({ refresh }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function load() {
    try { setData(await phoneApi.messages()); setError('') } catch (err) { setError(err.message) }
  }
  useEffect(() => { load(); const id = setInterval(load, 10000); return () => clearInterval(id) }, [refresh])
  async function test() {
    setBusy(true); setError('')
    try { await phoneApi.testSms(); await load() } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <Card><div className="flex flex-wrap items-center justify-between gap-3">
    <h2 className="text-lg font-semibold">{data?.sms_mode === 'simulated' ? 'Simulated SMS inbox' : 'SMS delivery activity'}</h2>
    <Button variant="ghost" onClick={load}>Refresh inbox</Button></div>
    <p className="my-3 text-xs leading-relaxed text-slate-400">{data?.sms_mode === 'simulated'
      ? 'Private test messages for your account. No text message is sent to a real phone. These messages are from BridgeEscrow, not Safaricom.'
      : 'Provider SMS is queued for delivery to your phone. Accepted means the provider accepted the message; handset delivery is not yet confirmed.'}</p>
    <Alert>{error}</Alert><Button variant="ghost" onClick={test} disabled={busy}>Send test SMS to my verified phone</Button>
    <ul className="mt-4 divide-y divide-white/10">{data?.messages.map((message) => <li key={message.id} className="space-y-2 py-3 text-sm">
      <p className="text-xs text-slate-500">+{message.phone} · {message.status} · {new Date(message.created_at + 'Z').toLocaleString()}</p>
      {message.body && <p className="whitespace-pre-wrap text-slate-200">{message.body}</p>}
    </li>)}</ul>{data && !data.messages.length && <p className="mt-4 text-sm text-slate-400">No messages yet.</p>}
  </Card>
}
