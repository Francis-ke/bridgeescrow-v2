import { Link } from 'react-router-dom'
import NotificationItem from './NotificationItem'
export default function NotificationPanel({ feed, filter, setFilter, onView, onClose }) {
  const { items, count, loading, busy, error, readAll, retry } = feed
  const visible = filter === 'unread' ? items.filter((item) => !item.read) : items
  return <section id="notifications-panel" aria-label="Notifications"
    className="absolute -right-[52px] top-full z-50 mt-4 w-96 max-w-[calc(100vw-2rem)] overflow-hidden rounded-2xl border border-white/10 bg-navy-800 shadow-[0_24px_70px_rgba(0,0,0,0.45)]">
    <div className="flex items-center justify-between gap-3 px-5 pb-4 pt-5">
      <div><h2 className="text-base font-semibold text-white">Notifications</h2>
        <p aria-live="polite" className="mt-1 text-xs text-slate-400">{count ? `${count} unread ${count === 1 ? 'update' : 'updates'}` : 'You’re all caught up'}</p></div>
      <button type="button" aria-label="Close notifications" onClick={onClose} className="rounded-lg p-2 text-slate-500 hover:bg-white/5 hover:text-white">×</button>
    </div>
    <div className="flex items-center justify-between border-b border-white/10 px-5 pb-3">
      <div className="flex gap-1 rounded-lg bg-navy-900/60 p-1" aria-label="Filter notifications">
        {['all', 'unread'].map((value) => <button type="button" key={value} aria-pressed={filter === value} onClick={() => setFilter(value)}
          className={`rounded-md px-3 py-1.5 text-xs font-medium capitalize ${filter === value ? 'bg-teal-400/15 text-teal-300' : 'text-slate-500 hover:text-slate-200'}`}>{value}</button>)}
      </div>
      <button type="button" disabled={!count || busy} onClick={readAll} className="text-xs font-medium text-teal-300 disabled:text-slate-600">Mark all read</button>
    </div>
    {error && <div role="alert" className="m-3 rounded-xl bg-red-400/5 p-3 text-xs text-red-300">{error}<button type="button" onClick={retry} className="ml-2 underline">Retry</button></div>}
    {!error && loading && <p className="p-6 text-center text-sm text-slate-500">Loading updates…</p>}
    {!error && !loading && !visible.length && <div className="px-6 py-10 text-center">
      <span aria-hidden="true" className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-teal-400/10 text-xl text-teal-300">✓</span>
      <p className="text-sm font-medium text-slate-300">{filter === 'unread' ? 'All caught up' : 'No updates yet'}</p>
      <p className="mt-2 text-xs text-slate-500">Your payment and account updates will appear here.</p>
    </div>}
    <ul className="max-h-[55vh] space-y-1 overflow-y-auto p-2">{visible.map((item) => <NotificationItem key={item.id} item={item} onView={onView} busy={busy} />)}</ul>
    <Link to="/?statements=1" onClick={onClose} className="flex items-center justify-between border-t border-white/10 px-5 py-4 text-xs font-medium text-teal-300">View wallet activity <span aria-hidden="true">→</span></Link>
  </section>
}
