import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDisclosure } from '../hooks/useDisclosure'
import { useNotifications } from '../hooks/useNotifications'
import NotificationPanel from './NotificationPanel'
export default function NotificationBell() {
  const { open, setOpen, ref } = useDisclosure()
  const [filter, setFilter] = useState('all')
  const feed = useNotifications(open)
  const navigate = useNavigate()
  async function view(item) {
    if (await feed.read(item)) {
      setOpen(false); navigate(item.url || (item.escrow_id ? `/escrows/${item.escrow_id}` : '/?statements=1'))
    }
  }
  return <div ref={ref} className="relative">
    <button type="button" onClick={() => setOpen(!open)} aria-label={`Notifications, ${feed.count} unread`}
      aria-expanded={open} aria-controls="notifications-panel"
      className={`relative flex h-10 w-10 items-center justify-center rounded-xl border transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-teal-400 ${open ? 'border-teal-400/40 bg-teal-400/10 text-teal-300' : 'border-white/10 bg-white/[0.02] text-slate-300 hover:border-teal-400/30 hover:text-teal-300'}`}>
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>
      <span aria-hidden="true" className="absolute -right-1.5 -top-1.5 flex h-5 min-w-5 items-center justify-center rounded-full border-2 border-navy-900 bg-teal-400 px-1 text-[10px] font-bold text-navy-900">{feed.count > 99 ? '99+' : feed.count}</span>
    </button>
    {open && <NotificationPanel feed={feed} filter={filter} setFilter={setFilter} onView={view} onClose={() => setOpen(false)} />}
  </div>
}
