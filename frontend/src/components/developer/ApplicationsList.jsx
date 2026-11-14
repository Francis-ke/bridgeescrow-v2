export default function ApplicationsList({ applications, selected, onSelect, loading }) {
  return <section className="rounded-2xl border border-white/10 bg-navy-800/60 p-5">
    <h2 className="mb-4 text-lg font-semibold">My Applications</h2>
    {loading && <p className="text-sm text-slate-400">Loading applications…</p>}
    {!loading && !applications.length && <p className="text-sm text-slate-400">Create your first application to generate sandbox credentials.</p>}
    <ul className="space-y-2">{applications.map((app) => <li key={app.id}>
      <button type="button" onClick={() => onSelect(app.id)} aria-pressed={selected === app.id}
        className={`w-full rounded-xl border p-4 text-left transition ${selected === app.id ? 'border-teal-400/40 bg-teal-400/10' : 'border-white/10 hover:border-teal-400/20'}`}>
        <span className="flex items-center justify-between gap-3"><span className="font-medium">{app.name}</span>
          <span className={`rounded-full px-2 py-1 text-[10px] ${app.active ? 'bg-teal-400/10 text-teal-300' : 'bg-slate-500/10 text-slate-500'}`}>{app.active ? 'Active' : 'Inactive'}</span></span>
        <span className="mt-2 block break-all font-mono text-[10px] text-slate-500">{app.app_id}</span>
        <span className="mt-1 block text-xs text-slate-400">{app.environment} · {app.type}</span>
      </button>
    </li>)}</ul>
  </section>
}
