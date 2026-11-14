import HoldDecision from './HoldDecision'
import { Link } from 'react-router-dom'
import TransactionDetails from './TransactionDetails'
import ReceiptHoldForm from './ReceiptHoldForm'

const TONE = {
  hold: 'text-amber-300', funded: 'text-teal-300', released: 'text-emerald-300',
  refunded: 'text-slate-300', disputed: 'text-red-300', cancelled: 'text-slate-500',
}

export default function EscrowRow({ escrow, onUpdate }) {
  return (
    <li className="py-4 text-sm">
      <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
        <Link to={`/escrows/${escrow.id}`} className="min-w-0">
          <p className="truncate font-medium text-white">{escrow.title}</p>
          {escrow.protection && <p className="text-xs text-teal-300">{escrow.protection.label} · {escrow.protection.state.replaceAll("_", " ")}</p>}
          <p className="text-xs text-slate-500">{escrow.reference}</p>
        </Link>
        <div className="sm:text-right">
          <p className="font-semibold">KES {escrow.amount}</p>
          <p className={`text-xs uppercase ${TONE[escrow.status] || 'text-slate-400'}`}>{escrow.status}</p>
        </div>
      </div>
      <details className="mt-3 rounded-xl border border-white/10 bg-navy-900/40 p-3">
        <summary className="cursor-pointer text-xs font-medium text-teal-300 focus-visible:outline focus-visible:outline-teal-400">
          Transaction details
        </summary>
        <div className="mt-4"><TransactionDetails escrow={escrow} /></div>
        <ReceiptHoldForm escrow={escrow} onUpdate={onUpdate} />
      </details>
      <HoldDecision escrow={escrow} onUpdate={onUpdate} />
    </li>
  )
}
