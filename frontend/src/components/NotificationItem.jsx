const icons = {
  deposit: 'M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4',
  incoming: 'M19 5 5 19M5 7v12h12',
  received: 'm5 12 4 4L19 6',
  refund: 'M8 3 3 8l5 5M3 8h10a7 7 0 0 1 0 14',
  hold: 'M12 8v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
}

export default function NotificationItem({ item, onView, busy }) {
  const fullTime = new Date(item.created_at).toLocaleString('en-KE', { timeZone: 'Africa/Nairobi' }) + ' EAT'
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(item.created_at).getTime()) / 1000))
  const age = seconds < 60 ? 'Just now' : seconds < 3600 ? `${Math.floor(seconds / 60)} min ago`
    : seconds < 86400 ? `${Math.floor(seconds / 3600)} hr ago`
      : new Date(item.created_at).toLocaleDateString('en-KE', { day: 'numeric', month: 'short', timeZone: 'Africa/Nairobi' })
  return (
    <li>
      <button type="button" disabled={busy} onClick={() => onView(item)}
        className={`group flex w-full gap-3 rounded-xl p-3.5 text-left transition hover:bg-white/5 focus-visible:outline focus-visible:outline-inset focus-visible:outline-teal-400 disabled:opacity-50 ${item.read ? '' : 'bg-teal-400/[0.04]'}`}>
        <span className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border ${item.kind === 'hold' ? 'border-amber-300/15 bg-amber-300/10 text-amber-300' : 'border-teal-400/15 bg-teal-400/10 text-teal-300'}`}>
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={icons[item.kind] || icons.received} /></svg>
        </span>
        <span className="min-w-0 flex-1">
          <span className="flex items-center justify-between gap-2">
            <span className={`text-sm font-semibold ${item.read ? 'text-slate-400' : 'text-slate-100'}`}>{item.title || 'Account update'}</span>
            {!item.read && <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-teal-400"><span className="sr-only">Unread</span></span>}
          </span>
          <span className="mt-1 block break-words text-xs leading-relaxed text-slate-400">{item.message}</span>
          <time dateTime={item.created_at} title={fullTime} className="mt-2 block text-[10px] text-slate-500">{age}</time>
        </span>
      </button>
    </li>
  )
}
