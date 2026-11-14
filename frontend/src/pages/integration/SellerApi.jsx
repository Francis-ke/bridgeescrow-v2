import { useEffect, useState } from 'react'
import { sellerApi as api } from '../../api/integrations'
import { useAuth } from '../../context/AuthContext'
import { Alert, Card } from '../../components/ui'
import ApiKeyForm from '../../components/integration/ApiKeyForm'
import ApiKeys from '../../components/integration/ApiKeys'
import IntegrationGuide from '../../components/integration/IntegrationGuide'
import CreateOrder from '../../components/integration/CreateOrder'
import SellerOrders from '../../components/integration/SellerOrders'
export default function SellerApi() {
  const { user, signIn } = useAuth()
  const [settings, setSettings] = useState(null)
  const [orders, setOrders] = useState([])
  const [secret, setSecret] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function load() {
    const [config, result] = await Promise.all([api.settings(), api.orders()])
    setSettings(config); setOrders(result.orders)
  }
  useEffect(() => { load().catch((err) => setError(err.message)) }, [])
  async function run(action) {
    if (busy) return
    setBusy(true); setError('')
    try { await action(); await load(); window.dispatchEvent(new Event('account-updated')) }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  async function createKey(body) {
    const result = await api.createKey(body)
    setSecret(result.secret); signIn(result.session)
  }
  return <div className="mx-auto max-w-3xl space-y-5">
    <h1 className="text-2xl font-semibold">Existing website integrations</h1><Alert>{error}</Alert>
    {settings && <>
      <Card><ApiKeyForm initial={settings.profile} email={user.email} busy={busy} onCreate={(body) => run(() => createKey(body))} /></Card>
      <Card><ApiKeys keys={settings.keys} secret={secret} busy={busy} onRevoke={(id) => run(() => api.revoke(id))} /></Card>
      <Card><IntegrationGuide /></Card>
      {settings.profile && <Card><CreateOrder busy={busy} onCreate={(body) => run(() => api.createOrder(body))} /></Card>}
      <Card><SellerOrders orders={orders} busy={busy} redeem={(id, code) => run(() => api.redeem(id, code))} /></Card>
    </>}
  </div>
}
