import { Link } from 'react-router-dom'

const actions = [
  { label: 'Buy goods and services', to: '/payments/buy', icon: 'M4 8h16l-2 12H6L4 8Zm4 0V6a4 4 0 0 1 8 0v2M9 12v4m6-4v4' },
  { label: 'Send money', to: '/payments/send', icon: 'm21 3-7 18-4-7-7-4L21 3ZM10 14 21 3' },
  { label: 'Deposit', to: '/wallet/deposit', icon: 'M4 13V4h16v9M8 8h8M12 21v-8m-4 4 4-4 4 4' },
  { label: 'Withdraw', to: '/wallet/withdraw', icon: 'M4 13V4h16v9M8 8h8M8 12h2m2 1v8m-4-4 4 4 4-4' },
]

export default function QuickActions() {
  return (
    <nav aria-label="Payment shortcuts" className="grid grid-cols-2 gap-3 sm:grid-cols-4 sm:gap-4">
      {actions.map(({ label, to, icon }) => <Link key={to} to={to}
        className="group flex min-h-[140px] flex-col items-center justify-center gap-3 rounded-2xl border border-white/[0.08] bg-navy-800/50 px-3 py-5 text-center transition hover:border-teal-400/30 hover:bg-navy-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-400">
        <span className="flex h-14 w-14 items-center justify-center rounded-full border border-teal-400/15 bg-teal-400/10 text-teal-400 transition duration-200 motion-safe:group-hover:-translate-y-1 group-hover:border-teal-400/40 group-hover:bg-teal-400/20 sm:h-14 sm:w-14">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={icon} /></svg>
        </span>
        <span className="max-w-36 text-xs font-medium leading-relaxed text-slate-200 transition group-hover:text-teal-300 sm:text-sm">{label}</span>
      </Link>)}
    </nav>
  )
}
