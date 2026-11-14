import { dateTime, money } from './format'
export default function ProtectedSummary({ payment: p }) {
  const rows = [['Client', p.escrow.buyer], ['Provider', p.escrow.seller],
    ['Total', money(p.escrow.amount)], ['Released', money(p.released)],
    ['Refunded', money(p.refunded)], ['Deadline', dateTime(p.deadline)],
    ['Client acceptance', p.client_accepted ? 'Accepted' : 'Pending'],
    ['Provider acceptance', p.provider_accepted ? 'Accepted' : 'Pending'],
    ['Release rule', p.rules.release.replaceAll('_', ' ')],
    ['Cancellation deadline', dateTime(p.rules.cancellation_deadline)],
    ['Refund before / after deadline', `${p.rules.early_refund_percent}% / ${p.rules.late_refund_percent}%`],
    ['Maximum extension', `${p.rules.max_extension_hours} hours`]]
  if (p.category === 'booking') rows.push(['Booking starts', dateTime(p.booking_start)],
    ['Booking ends', dateTime(p.booking_end)], ['Reservation', p.reservation_confirmed_at ? 'Confirmed' : 'Awaiting provider'])
  return <section className="space-y-4">
    <div className="flex flex-wrap items-center gap-3"><span className="rounded-full bg-teal-400/10 px-3 py-1 text-xs text-teal-300">{p.label}</span>
      <span className="text-xs capitalize text-slate-400">{p.state.replaceAll('_', ' ')}</span></div>
    <h1 className="text-2xl font-semibold">{p.escrow.title}</h1>
    <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">{p.description}</p>
    {p.overdue && <p role="status" className="text-sm text-amber-300">The agreed deadline has passed. Request an extension, cancellation, or dispute; funds do not release automatically.</p>}
    <dl className="grid gap-4 text-sm sm:grid-cols-2">{rows.map(([label, value]) => <div key={label}>
      <dt className="text-xs text-slate-500">{label}</dt><dd className="mt-1 text-slate-200">{value}</dd>
    </div>)}</dl>
    {p.category === 'booking' && <p className="rounded-lg border border-teal-400/20 p-3 text-xs text-teal-300">Booking uses the refund percentages agreed above, not a general 80/20 rule. Provider cancellation refunds remaining secured funds in full.</p>}
  </section>
}
