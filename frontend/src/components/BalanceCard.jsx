import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function BalanceCard({ title, amount, description, action, to, onClick }) {
  const [hidden, setHidden] = useState(false)
  const money = amount == null ? '—' : Number(amount).toLocaleString('en-KE', {
    minimumFractionDigits: 2, maximumFractionDigits: 2,
  })
  const actionClass = 'group inline-flex items-center gap-2 rounded-md text-xs font-semibold text-teal-300 transition hover:text-teal-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-400'
  const actionContent = <>{action}<span aria-hidden="true" className="transition-transform motion-safe:group-hover:translate-x-1">→</span></>

  return (
    <section className="relative flex min-w-0 items-start gap-4 overflow-hidden rounded-2xl border border-white/[0.08] bg-gradient-to-br from-navy-800 to-navy-800/40 p-4 shadow-sm transition hover:border-teal-400/20 sm:p-5">
      <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${to ? 'border-cyan-300/15 bg-cyan-300/10 text-cyan-300' : 'border-teal-400/15 bg-teal-400/10 text-teal-400'}`}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          {to ? <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" /><path d="m8.5 12 2.5 2.5 4.5-5" /></>
            : <><rect x="3" y="5" width="18" height="15" rx="3" /><path d="M3 9h18M16 13h5v4h-5a2 2 0 0 1 0-4Z" /></>}
        </svg>
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-xs font-medium tracking-wide text-slate-400">{title}</h2>
          <button type="button" onClick={() => setHidden(!hidden)}
            aria-label={`${hidden ? 'Show' : 'Hide'} ${title.toLowerCase()}`} aria-pressed={hidden}
            className="-my-1 shrink-0 rounded-md p-1 text-slate-500 transition hover:bg-white/5 hover:text-teal-300 focus-visible:outline focus-visible:outline-teal-400">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
              <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
              <circle cx="12" cy="12" r="3" />{!hidden && <path d="m3 21 18-18" />}
            </svg>
          </button>
        </div>
        <p className="mt-1 flex flex-wrap items-baseline gap-x-2 font-semibold tracking-tight text-white">
          <span className="text-xs font-medium text-slate-500">KES</span>
          <span className="text-2xl tabular-nums">{hidden ? '••••••' : money}</span>
        </p>
        <p className="mt-1 text-[11px] leading-relaxed text-slate-500">{description}</p>
        <div className="mt-3">{to ? <Link to={to} className={actionClass}>{actionContent}</Link>
          : <button type="button" onClick={onClick} className={actionClass}>{actionContent}</button>}</div>
      </div>
    </section>
  )
}
