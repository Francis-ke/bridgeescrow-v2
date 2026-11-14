import { useEffect, useState } from 'react'
import { escrows } from '../api/endpoints'

const EMPTY = { terms: '', delivery_days: 7 }

export default function ContractPanel({ escrowId, status }) {
  const [c, setC] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [msg, setMsg] = useState('')

  const load = () => escrows.contract(escrowId).then((d) => setC(d.contract))
  useEffect(() => { load() }, [escrowId])

  async function save(e) {
    e.preventDefault()
    setC((await escrows.saveContract(escrowId, form)).contract)
    setMsg('Draft saved.')
  }

  return (
    <div className="mt-4 border-t border-white/10 pt-4">
      <h3 className="mb-2 font-semibold">Contract</h3>
      {c ? (
        <div className="space-y-1 text-sm">
          <p className="text-slate-300">{c.terms}</p>
          <p className="text-xs text-slate-500">Delivery within {c.delivery_days} days</p>
          <p className="text-xs">
            Buyer {c.buyer_signed ? '✅' : '—'} · Seller {c.seller_signed ? '✅' : '—'}
          </p>
          <button onClick={async () => { setC((await escrows.signContract(escrowId)).contract) }}
            className="mt-2 rounded-lg border border-white/20 px-3 py-1 text-sm">Sign contract</button>
        </div>
      ) : status === 'hold' ? (
        <form onSubmit={save} className="space-y-2">
          <textarea value={form.terms} onChange={(e) => setForm({ ...form, terms: e.target.value })}
            placeholder="Describe exactly what is delivered…" rows={3}
            className="w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-sm" />
          <button className="rounded-lg bg-teal-500 px-3 py-1 text-sm font-semibold text-navy-900">Save draft</button>
        </form>
      ) : <p className="text-sm text-slate-500">No contract attached.</p>}
      {msg && <p className="mt-2 text-xs text-teal-300">{msg}</p>}
    </div>
  )
}
