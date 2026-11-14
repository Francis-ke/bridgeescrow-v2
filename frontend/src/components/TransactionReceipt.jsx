import { useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'

export default function TransactionReceipt({ title, receipt, onAgain }) {
  const heading = useRef(null)
  useEffect(() => { heading.current?.focus() }, [])
  const rows = [
    ['Amount', `KES ${Number(receipt.amount).toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
    ['Method', receipt.method === 'card' ? `Card •••• ${receipt.last4}` : 'M-PESA'],
    ['Reference', receipt.reference],
    ['Time', new Date(receipt.createdAt).toLocaleString('en-KE', { timeZone: 'Africa/Nairobi' }) + ' EAT'],
  ]
  if (receipt.destination) rows.splice(1, 0, [receipt.kind === 'send' ? 'Receiving account' : 'Recipient / destination', receipt.destination])
  return (
    <section className="rounded-2xl border border-teal-400/20 bg-navy-800 p-6 text-center sm:p-8">
      <span aria-hidden="true" className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-teal-400/15 text-3xl text-teal-400">✓</span>
      <h2 ref={heading} tabIndex={-1} className="text-xl font-semibold outline-none">Transaction completed</h2>
      <p className="mt-2 text-sm text-slate-400">{title} completed successfully.</p>
      <dl className="my-6 divide-y divide-white/10 text-left text-sm">{rows.map(([label, value]) => <div key={label} className="flex min-w-0 flex-col justify-between gap-1 py-3 sm:flex-row sm:gap-2">
        <dt className="text-slate-500">{label}</dt><dd className="min-w-0 break-words text-slate-200 sm:text-right">{value}</dd>
      </div>)}</dl>
      <p className="mb-5 text-xs leading-relaxed text-slate-400">Your balance and transaction history have been updated.</p>
      {receipt.kind === 'send' && !receipt.escrow_id && <p className="mb-4 text-sm text-teal-300">Money credited directly to the recipient’s wallet.</p>}
      {receipt.escrow_id && <p className="mb-4 text-xs leading-relaxed text-teal-300">Funds are held in escrow. The recipient receives them after the buyer confirms release.</p>}
      {receipt.escrow_id && <Link to={`/escrows/${receipt.escrow_id}`} className="mb-4 block text-sm text-teal-300">View protected transaction →</Link>}
      <button type="button" onClick={onAgain} className="w-full rounded-xl bg-teal-400 px-4 py-3 text-sm font-semibold text-navy-900 hover:bg-teal-300">Make another transaction</button>
      <Link to="/" className="mt-4 inline-block text-sm text-teal-300">Back to home</Link>
    </section>
  )
}
