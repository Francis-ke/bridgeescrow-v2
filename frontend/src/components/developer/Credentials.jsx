import { useEffect, useState } from 'react'
import { developerApi as api } from '../../api/developer'
import { Alert, Button, Field } from '../ui'
import CredentialSecret from './CredentialSecret'
import KeyPermissions, { permissions } from './KeyPermissions'
import CopyValue from './CopyValue'
export default function Credentials({ application }) {
  const [keys, setKeys] = useState([])
  const [revealed, setRevealed] = useState(null)
  const [name, setName] = useState('Server integration')
  const [selected, setSelected] = useState(permissions)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function load() { setKeys((await api.keys(application.id)).credentials) }
  useEffect(() => {
    setRevealed(null); setKeys([])
    load().catch((err) => setError(err.message))
  }, [application.id])
  useEffect(() => { if (!application.active) setRevealed(null) }, [application.active])
  async function run(task, secret = false) {
    setBusy(true); setError('')
    try { const result = await task(); if (secret) setRevealed(result);
      else if (result.credential?.id === revealed?.credential.id) setRevealed(null)
      await load() }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <section className="space-y-4 rounded-2xl border border-white/10 bg-navy-800/60 p-5">
    <h2 className="text-lg font-semibold">API Credentials</h2>
    <p className="text-xs leading-relaxed text-slate-400">Use secret keys only on your backend server. Keys identify this application and its linked merchant account. Permissions limit what each key can do. Keep live and sandbox credentials separate.</p>
    <Alert>{error}</Alert>
    {revealed && <CredentialSecret value={revealed} onDismiss={() => setRevealed(null)} />}
    <form onSubmit={(event) => { event.preventDefault(); run(() => api.createKey(application.id, { name, permissions: selected }), true) }} className="space-y-4">
      <Field label="Credential name" value={name} required maxLength={80} onChange={(event) => setName(event.target.value)} />
      <KeyPermissions value={selected} onChange={setSelected} />
      <Button type="submit" disabled={busy || !application.active || !selected.length}>{busy ? 'Please wait…' : 'Generate credentials'}</Button>
    </form>
    <ul className="space-y-3">{keys.map((key) => <li key={key.id} className="space-y-3 rounded-xl border border-white/10 p-4">
      <div className="flex justify-between gap-2 text-sm"><span>{key.name || 'API credential'}</span><span className={key.active ? 'text-teal-300' : 'text-slate-500'}>{key.active ? 'Active' : 'Revoked'}</span></div>
      <CopyValue label="Public key" value={key.public_key} />
      <p className="break-all font-mono text-xs text-slate-500">Secret: {key.prefix}••••</p>
      <p className="text-xs text-slate-400">{key.permissions.join(' · ')}</p>
      {key.active && <div className="flex gap-3">
        <Button variant="ghost" disabled={busy || !application.active} onClick={() => run(() => api.rotateKey(key.id), true)}>Rotate key</Button>
        <Button variant="ghost" disabled={busy} onClick={() => run(() => api.revokeKey(key.id))}>Revoke key</Button>
      </div>}
    </li>)}</ul>
  </section>
}
