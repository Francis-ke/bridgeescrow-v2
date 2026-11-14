import { useEffect, useState } from 'react'
import { escrows } from '../api/endpoints'

export default function DisputePanel({ escrow, reload }) {
  const [rows, setRows] = useState([])
  const [reason, setReason] = useState('')
  const [err, setErr] = useState('')

  const load = () => escrows.disputes(escrow.id).then((d) => setRows(d.disputes))
  useEffect(() => { load() }, [escrow.id])

  async function raise(e) {
    e.preventDefault()
    setErr('')
    try {
      await escrows.dispute(escrow.id, reason)
      setReason(''); load(); reload()
    } catch (e2) { setErr(e2.message) }
  }

  return (
    <div className="mt-4 border-t border-white/10 pt-4">
      <h3 className="mb-2 font-semibold">Disputes</h3>
      {err && <p className="mb-2 text-sm text-red-300">{err}</p>}
      <ul className="mb-3 space-y-2 text-sm">
        {rows.map((d) => (
          <li key={d.id} className="rounded-lg bg-navy-900 p-2">
            <p className="text-slate-300">{d.reason}</p>
            <p className="text-xs text-slate-500">{d.status}{d.resolution ? ` — ${d.resolution}` : ''}</p>
          </li>
        ))}
        {rows.length === 0 && <li className="text-slate-500">No disputes raised.</li>}
      </ul>
      {['funded', 'disputed'].includes(escrow.status) && (
        <form onSubmit={raise} className="flex gap-2">
          <input value={reason} onChange={(e) => setReason(e.target.value)}
            placeholder="Explain the problem (10+ chars)"
            className="flex-1 rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-sm" />
          <button className="rounded-lg border border-white/20 px-3 py-2 text-sm">Raise dispute</button>
        </form>
      )}
    </div>
  )
}
