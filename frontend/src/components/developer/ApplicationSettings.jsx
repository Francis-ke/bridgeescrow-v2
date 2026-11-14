import { useState } from 'react'
import { developerApi as api } from '../../api/developer'
import { Alert, Button } from '../ui'
import ApplicationForm from './ApplicationForm'
import CopyValue from './CopyValue'
export default function ApplicationSettings({ application, onChange }) {
  const [editing, setEditing] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function save(body) {
    setBusy(true); setError('')
    try { const result = await api.editApp(application.id, body); onChange(result.application); setEditing(false); return true }
    catch (err) { setError(err.message); return false } finally { setBusy(false) }
  }
  return <section className="space-y-4 rounded-2xl border border-white/10 bg-navy-800/60 p-5">
    <div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-lg font-semibold">Application details</h2>
      <Button variant="ghost" disabled={busy} onClick={() => setEditing(!editing)}>{editing ? 'Close settings' : 'Edit settings'}</Button></div>
    <Alert>{error}</Alert><CopyValue label="Application ID" value={application.app_id} />
    <div className="space-y-2 rounded-xl border border-teal-400/20 bg-teal-400/5 p-4">
      <h3 className="text-sm font-semibold text-teal-200">Linked merchant account</h3>
      {application.owner && <p className="text-sm text-slate-200">{application.owner.name} · {application.owner.account_number}</p>}
      <p className="text-xs leading-relaxed text-slate-400">Every secret key generated for this application identifies this account as the merchant. Your server uses that key to create orders; customers do not enter your account number or select a recipient.</p>
      <p className="text-xs leading-relaxed text-amber-200">{application.environment === 'production' ? 'Live M-PESA payments appear in your account Escrow Balance, then Available Balance after buyer-approved release, less fees.' : 'Sandbox payments appear under this application’s Sandbox Environment. Released test funds stay in its simulated seller balance and do not credit your normal wallet.'}</p>
    </div>
    {editing ? <ApplicationForm key={application.id} application={application} onSave={save} busy={busy} /> : <>
      <p className="break-words text-sm text-slate-300">{application.description}</p>
      {application.website && <p className="break-all text-xs text-slate-400">{application.website}</p>}
      <p className="text-xs text-slate-500">{application.type} · {application.environment} · {application.active ? 'Active' : 'Inactive'}</p>
    </>}
    <Button variant="ghost" disabled={busy} onClick={() => save({ active: !application.active })}>
      {application.active ? 'Deactivate application' : 'Reactivate application'}
    </Button>
    {!application.active && <p className="text-xs text-amber-300">Inactive applications cannot authorize external API requests.</p>}
  </section>
}
