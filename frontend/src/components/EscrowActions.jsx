import { useState } from 'react'
import { escrows } from '../api/endpoints'

export default function EscrowActions({ escrow, reload }) {
  const [code, setCode] = useState('')
  const [testCode, setTestCode] = useState('')
  const [requested, setRequested] = useState(false)
  const [err, setErr] = useState('')

  const run = (fn) => fn().then(reload).catch((e) => setErr(e.message))

  return (
    <div className="mt-4 space-y-3 border-t border-white/10 pt-4">
      {err && <p className="text-sm text-red-300">{err}</p>}
      <div className="flex flex-wrap gap-2">
        {escrow.status === 'hold' && (
          <button onClick={() => run(() => escrows.fund(escrow.id))}
            className="rounded-lg bg-teal-500 px-3 py-2 text-sm font-semibold text-navy-900">
            Fund from wallet
          </button>
        )}
        {escrow.status === 'funded' && (
          <button disabled={escrow.transaction?.receipt_hold_active} onClick={() => run(async () => { const result = await escrows.release(escrow.id); setTestCode(result.demo_code || ''); setRequested(true) })}
            className="rounded-lg bg-teal-500 px-3 py-2 text-sm font-semibold text-navy-900">
            {escrow.transaction?.receipt_hold_active ? 'Recipient hold active' : 'Release funds'}
          </button>
        )}
        {['funded', 'disputed'].includes(escrow.status) && (
          <button onClick={() => run(() => escrows.refund(escrow.id))}
            className="rounded-lg border border-white/20 px-3 py-2 text-sm">Request refund</button>
        )}
      </div>
      {requested && <p className="text-xs text-slate-400">Enter the release code only after receiving and checking your order.</p>}
      {requested && (
        <div className="flex gap-2">
          <input value={code} onChange={(e) => setCode(e.target.value)} placeholder="6-digit code"
            className="flex-1 rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-sm" />
          <button onClick={() => run(() => escrows.confirm(escrow.id, code))}
            className="rounded-lg bg-teal-500 px-3 py-2 text-sm font-semibold text-navy-900">Confirm</button>
        </div>
      )}
      {testCode && <p className="text-xs text-slate-500">Release code: <b className="text-teal-400">{testCode}</b></p>}
    </div>
  )
}
