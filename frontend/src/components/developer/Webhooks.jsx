import { useEffect, useState } from 'react'
import { developerApi as api } from '../../api/developer'
import { Alert } from '../ui'
import WebhookForm from './WebhookForm'
import WebhookEndpoint from './WebhookEndpoint'
import CopyValue from './CopyValue'
export default function Webhooks({ application }) {
  const [webhooks, setWebhooks] = useState([])
  const [logs, setLogs] = useState({})
  const [secret, setSecret] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  async function load() { setWebhooks((await api.webhooks(application.id)).webhooks) }
  useEffect(() => { load().catch((err) => setError(err.message)) }, [application.id])
  async function run(task, reveal = false) {
    setBusy(true); setError(''); setMessage('')
    try {
      const result = await task()
      if (reveal) setSecret(result.signing_secret)
      await load(); return result
    } catch (err) { setError(err.message); return null } finally { setBusy(false) }
  }
  async function deliveryLogs(id) {
    const result = await run(() => api.deliveries(id))
    if (result) setLogs((current) => ({ ...current, [id]: result.deliveries }))
  }
  async function test(id) {
    if (await run(() => api.testWebhook(id))) { setMessage('Test event queued. The webhook worker will deliver and sign it.'); await deliveryLogs(id) }
  }
  async function retry(id) {
    if (await run(() => api.retryDelivery(id))) {
      setMessage('Delivery queued for retry.')
      for (const webhook of webhooks) if (logs[webhook.id]) await deliveryLogs(webhook.id)
    }
  }
  return <section className="space-y-5 rounded-2xl border border-white/10 bg-navy-800/60 p-5">
    <h2 className="text-lg font-semibold">Webhook Configuration</h2>
    <p className="text-xs leading-relaxed text-slate-400">Register a public HTTPS URL. Deliveries use HMAC-SHA256 signatures and unique event IDs. Private, localhost, and unsafe redirect destinations are rejected.</p>
    <Alert>{error}</Alert>{message && <p role="status" className="text-xs text-teal-300">{message}</p>}
    {secret && <div className="space-y-3 rounded-xl border border-amber-300/20 bg-amber-300/5 p-4">
      <p className="text-xs text-amber-200">Save this signing secret now. It is only shown once.</p>
      <CopyValue label="Webhook signing secret" value={secret} />
      <button type="button" onClick={() => setSecret('')} className="text-xs text-slate-400">Dismiss signing secret</button>
    </div>}
    {application.active && <WebhookForm busy={busy} onSave={(body) => run(() => api.createWebhook(application.id, body), true)} />}
    {webhooks.map((webhook) => <WebhookEndpoint key={webhook.id} webhook={webhook} busy={busy}
      onUpdate={(id, body) => run(() => api.editWebhook(id, body))}
      onRotate={(id) => run(() => api.rotateWebhook(id), true)} onTest={test} onLogs={deliveryLogs}
      deliveries={logs[webhook.id]} onRetry={retry} />)}
  </section>
}
