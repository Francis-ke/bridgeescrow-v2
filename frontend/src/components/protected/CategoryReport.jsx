import { money } from './format'
export default function CategoryReport({ rows }) {
  return <div className="overflow-x-auto"><table className="w-full text-left text-xs">
    <thead><tr className="border-b border-white/10 text-slate-400">{['Type', 'State', 'Count', 'Total', 'Released', 'Refunded', 'Fees'].map((label) => <th key={label} className="p-2">{label}</th>)}</tr></thead>
    <tbody>{rows.map((row, i) => <tr key={i} className="border-b border-white/5">
      <td className="p-2">{row.label}</td><td className="p-2">{row.state}</td><td className="p-2">{row.count}</td>
      {[row.amount_cents, row.released_cents, row.refunded_cents, row.fee_cents].map((n, index) => <td key={index} className="whitespace-nowrap p-2">{money(n / 100)}</td>)}
    </tr>)}</tbody>
  </table>{!rows.length && <p className="py-4 text-slate-400">No protected payments yet.</p>}</div>
}
