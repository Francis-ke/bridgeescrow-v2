import { useRef, useState } from 'react'
import { escrows } from '../api/endpoints'

export default function EscrowActions({ escrow, reload }) {
  const [code, setCode] = useState('')
  const [testCode, setTestCode] = useState('')
  const [requested, setRequested] = useState(false)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const pending = useRef(false)

  async function run(fn) {
    if (pending.current) return
    pending.current = true; setBusy(true); setErr('')
    try { await fn(); await reload() }
    catch (error) { setErr(error.message) }
    finally { pending.current = false; setBusy(false) }
  }

  return (
    <div aria-busy={busy} className="mt-4 space-y-3 border-t border-white/10 pt-4">
      {busy && <p role="status" className="text-sm text-teal-300">Processing transaction…</p>}
      {err && <p role="alert" className="text-sm text-red-300">{err}</p>}
      <div className="flex flex-wrap gap-2">
        {escrow.status === 'hold' && (
          <button disabled={busy} onClick={() => run(() => escrows.fund(escrow.id))}
            className="rounded-lg bg-teal-500 px-3 py-2 text-sm font-semibold text-navy-900">
            Fund from wallet
          </button>
        )}
        {escrow.status === 'funded' && (
          <button disabled={busy || escrow.transaction?.receipt_hold_active} onClick={() => run(async () => { const result = await escrows.release(escrow.id); setTestCode(result.demo_code || ''); setRequested(true) })}
            className="rounded-lg bg-teal-500 px-3 py-2 text-sm font-semibold text-navy-900">
            {escrow.transaction?.receipt_hold_active ? 'Recipient hold active' : 'Release funds'}
          </button>
        )}
        {['funded', 'disputed'].includes(escrow.status) && (
          <button disabled={busy} onClick={() => run(() => escrows.refund(escrow.id))}
            className="rounded-lg border border-white/20 px-3 py-2 text-sm">Request refund</button>
        )}
      </div>
      {requested && <p className="text-xs text-slate-400">Enter the release code only after receiving and checking your order.</p>}
      {requested && (
        <div className="flex flex-col gap-2 sm:flex-row">
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="6-digit code"
            className="min-w-0 flex-1 rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-sm" />
          <button disabled={busy} onClick={() => run(() => escrows.confirm(escrow.id, code))}
            className="rounded-lg bg-teal-500 px-3 py-2 text-sm font-semibold text-navy-900">Confirm</button>
        </div>
      )}
      {testCode && <p className="text-xs text-slate-500">Release code: <b className="text-teal-400">{testCode}</b></p>}
    </div>
  )
}
