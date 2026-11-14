import { useEffect, useState } from 'react'
import { developerApi as api } from '../../api/developer'
import { Alert, Button, Field } from '../ui'
export default function SandboxPanel({ application }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [codes, setCodes] = useState({})
  async function load() {
    setBusy(true); setError('')
    try { setData(await api.sandbox(application.id)) } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  useEffect(() => { load() }, [application.id])
  async function confirm(event, id) {
    event.preventDefault(); setBusy(true); setError('')
    try { await api.confirmDelivery(application.id, id, codes[id]); setCodes((values) => ({ ...values, [id]: '' })); await load() }
    catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <section className="space-y-4 rounded-2xl border border-teal-400/20 bg-teal-400/[0.03] p-5">
    <div className="flex items-center justify-between gap-3"><h2 className="text-lg font-semibold">Sandbox Environment</h2><Button variant="ghost" disabled={busy} onClick={load}>Refresh sandbox</Button></div>
    <p className="text-xs leading-relaxed text-slate-400">Sandbox card and M-PESA flows use the existing test processor. No live STK Push or bank charge occurs. This application's seller balance and held funds are isolated from your normal account.</p>
    <Alert>{error}</Alert>
    {data && <><div className="grid gap-3 sm:grid-cols-3">{[['Available', data.available], ['Held', data.held], ['Refunded', data.refunded]].map(([label, amount]) => <div key={label} className="rounded-xl border border-white/10 bg-navy-900/50 p-4">
      <p className="text-xs text-slate-500">{label}</p><p className="mt-2 font-semibold text-teal-300">KES {amount || '0.00'}</p>
    </div>)}</div><p className="text-xs text-slate-500">Production financial operations are disabled.</p>
      <ul className="divide-y divide-white/10">{data.transactions?.map((transaction) => <li key={transaction.id} className="space-y-3 py-3 text-xs">
        <div className="flex flex-wrap justify-between gap-2"><span className="font-mono text-slate-400">{transaction.order_id || transaction.id}</span><span>{transaction.state}</span><span>KES {transaction.amount}</span></div>
        {transaction.state === 'HELD' && <form onSubmit={(event) => confirm(event, transaction.id)} className="flex flex-wrap items-end gap-3">
          <Field label={`Delivery code for ${transaction.order_id || transaction.id}`} required inputMode="numeric" pattern="[0-9]{8}" maxLength={8} value={codes[transaction.id] || ''}
            onChange={(event) => setCodes({ ...codes, [transaction.id]: event.target.value })} />
          <Button type="submit" variant="ghost" disabled={busy}>Confirm delivery</Button>
          <p className="w-full text-slate-500">Enter the buyer's emailed code after they receive and check their package.</p>
        </form>}
      </li>)}</ul></>}
  </section>
}
