import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { get, post } from '../api/client'
import { useAuth } from '../context/AuthContext'
import { Alert, Button, Card } from '../components/ui'
export default function AdminPortal() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  async function load() {
    const [overview, users, merchants, disputes] = await Promise.all([
      get('/admin/overview'), get('/admin/users'), get('/admin/merchants'), get('/admin/disputes'),
    ])
    setData({ overview, users: users.users, merchants: merchants.merchants, disputes: disputes.disputes })
  }
  useEffect(() => { if (user?.role === 'admin') load().catch((err) => setError(err.message)) }, [user?.role])
  async function action(path) {
    setBusy(true); setError('')
    try { await post(path, {}); await load() } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  if (user?.role !== 'admin') return <Alert>Administrator access is required.</Alert>
  return <div className="space-y-6">
    <header><h1 className="text-2xl font-semibold">Administrator portal</h1><Link to="/admin/reports" className="mt-3 inline-block text-sm text-teal-300 underline">View payment reports</Link></header>
    <Alert>{error}</Alert>
    {data && <><div className="grid grid-cols-2 gap-3 sm:grid-cols-4">{['users', 'merchants', 'escrows', 'disputed'].map((key) => <Card key={key}><p className="text-xs capitalize text-slate-400">{key}</p><p className="mt-2 text-xl font-semibold">{data.overview[key]}</p></Card>)}</div>
      <Card><h2 className="text-lg font-semibold">Disputes</h2><ul className="divide-y divide-white/10">{data.disputes.map((row) => <li key={row.id} className="space-y-2 py-4 text-sm">
        <p>#{row.id} · {row.category} · {row.status}</p><p className="text-slate-400">{row.reason}</p>
        {row.protected ? <Link className="text-teal-300 underline" to={'/admin/payments/' + row.escrow_id}>Review payment and resolution</Link>
          : <p className="text-xs text-slate-500">Legacy escrow #{row.escrow_id}. Review through the administrator API before deciding a refund.</p>}
      </li>)}</ul>{!data.disputes.length && <p className="mt-3 text-sm text-slate-400">No disputes.</p>}</Card>
      <Card><h2 className="text-lg font-semibold">Merchant approvals</h2><ul className="divide-y divide-white/10">{data.merchants.map((row) => <li key={row.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
        <p>{row.business_name} · {row.status}</p>{row.status !== 'approved' && <Button disabled={busy} variant="ghost" onClick={() => action('/admin/merchants/' + row.id + '/approve')}>Approve merchant</Button>}
      </li>)}</ul></Card>
      <Card><h2 className="text-lg font-semibold">Accounts</h2><ul className="divide-y divide-white/10">{data.users.filter((row) => row.role !== 'system').map((row) => <li key={row.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
        <div><p>{row.full_name} · {row.account_number}</p><p className="mt-1 text-xs text-slate-400">{row.email} · {row.role} · {row.is_active ? 'Active' : 'Suspended'}</p></div>
        {row.role !== 'admin' && <Button disabled={busy} variant="ghost" onClick={() => action('/admin/users/' + row.id + '/suspend')}>{row.is_active ? 'Suspend account' : 'Reactivate account'}</Button>}
      </li>)}</ul></Card>
    </>}
  </div>
}
