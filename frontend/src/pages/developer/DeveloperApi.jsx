import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { phoneApi } from '../../api/phone'
import { developerApi as api } from '../../api/developer'
import { Alert } from '../../components/ui'
import ApplicationForm from '../../components/developer/ApplicationForm'
import ApplicationsList from '../../components/developer/ApplicationsList'
import ApplicationSettings from '../../components/developer/ApplicationSettings'
import Credentials from '../../components/developer/Credentials'
import Webhooks from '../../components/developer/Webhooks'
import SandboxPanel from '../../components/developer/SandboxPanel'
import ApiDocumentation from '../../components/developer/ApiDocumentation'
import IntegrationGuide from '../../components/developer/IntegrationGuide'
export default function DeveloperApi() {
  const [liveEnabled, setLiveEnabled] = useState(false)
  useEffect(() => { phoneApi.status().then((data) => setLiveEnabled(data.developer_live_enabled)).catch(() => {}) }, [])
  const [applications, setApplications] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    api.apps().then((data) => {
      if (active) { setApplications(data.applications); setSelected(data.applications[0]?.id ?? null) }
    }).catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])
  function changed(application) {
    setApplications((current) => current.map((item) => item.id === application.id ? application : item))
  }
  async function create(body) {
    setBusy(true); setError('')
    try {
      const data = await api.createApp(body)
      setApplications((current) => [...current, data.application]); setSelected(data.application.id)
      return true
    } catch (err) { setError(err.message); return false } finally { setBusy(false) }
  }
  const application = applications.find((item) => item.id === selected)
  return <div className="space-y-7">
    <header className="rounded-2xl border border-teal-400/15 bg-gradient-to-br from-navy-800 to-navy-900 p-6 sm:p-8">
      <p className="text-xs font-medium uppercase tracking-[0.2em] text-teal-300">Build with BridgeEscrow</p>
      <h1 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">Developer API</h1>
      <p className="mt-3 max-w-2xl text-sm leading-relaxed text-slate-400">Let customers pay through a protected checkout from your website or app. Your server creates the order, BridgeEscrow hosts the payment steps, and verified updates keep your shop informed while funds are held until buyer confirmation. Explore the complete flow with simulated payments in the sandbox.</p>
      <span className="mt-4 inline-block rounded-full border border-amber-300/20 bg-amber-300/5 px-3 py-1 text-xs text-amber-200">{liveEnabled ? 'Sandbox and live M-PESA applications' : 'Sandbox only · Production disabled'}</span>
      <Link to="/developers/api/legacy" className="mt-4 block text-xs text-slate-400 underline hover:text-teal-300">Manage existing website integrations</Link>
    </header>
    <IntegrationGuide liveEnabled={liveEnabled} />
    <Alert>{error}</Alert>
    <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
      <div className="space-y-6">
        <section className="rounded-2xl border border-white/10 bg-navy-800/60 p-5"><h2 className="mb-4 text-lg font-semibold">Create Application</h2><ApplicationForm allowProduction={liveEnabled} onSave={create} busy={busy} /></section>
        <ApplicationsList applications={applications} selected={selected} onSelect={setSelected} loading={loading} />
      </div>
      {application ? <div key={application.id} className="space-y-6">
        <ApplicationSettings application={application} onChange={changed} />
        <Credentials application={application} />
        <Webhooks application={application} />
        {application.environment === 'production' ? <p className="rounded-xl border border-teal-400/20 p-5 text-sm text-teal-200">Live orders appear in your account's Escrow Balance while held and Available Balance after release. <Link to="/">View My wallet</Link></p> : <SandboxPanel application={application} />}
      </div> : <div className="rounded-2xl border border-dashed border-white/10 p-8 text-center text-sm text-slate-500">Select or create an application to manage credentials and webhooks.</div>}
    </div>
    <ApiDocumentation application={application} />
  </div>
}
