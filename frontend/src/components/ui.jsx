export const cx = (...c) => c.filter(Boolean).join(' ')

export function Card({ children, className = '' }) {
  return (
    <div className={cx('rounded-2xl border border-white/10 bg-navy-800/70 p-6 shadow-xl', className)}>
      {children}
    </div>
  )
}

export function Field({ label, ...props }) {
  return (
    <label className="block text-sm">
      <span className="mb-1 block text-slate-300">{label}</span>
      <input
        {...props}
        className="w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2 text-white
                   outline-none placeholder:text-slate-500 focus:border-teal-400"
      />
    </label>
  )
}

export function Button({ children, variant = 'primary', className = '', ...props }) {
  const styles = {
    primary: 'bg-teal-500 text-navy-900 hover:bg-teal-400',
    ghost: 'border border-white/15 text-white hover:bg-white/5',
  }
  return (
    <button
      {...props}
      className={cx('rounded-lg px-4 py-2 text-sm font-semibold transition disabled:opacity-50',
        styles[variant], className)}
    >
      {children}
    </button>
  )
}

export function Alert({ children }) {
  if (!children) return null
  return <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-300">{children}</p>
}

export function Kpi({ label, value, sub }) {
  return (
    <Card>
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-white">{value}</p>
      {sub && <p className="text-xs text-slate-500">{sub}</p>}
    </Card>
  )
}
