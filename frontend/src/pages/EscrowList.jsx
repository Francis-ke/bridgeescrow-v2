import { useEffect, useState } from 'react'
import { Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { escrows } from '../api/endpoints'
import { Alert, Card } from '../components/ui'
import EscrowRow from '../components/EscrowRow'

export default function EscrowList({ received = false }) {
  const [params, setParams] = useSearchParams()
  const navigate = useNavigate()
  const direction = received ? 'received' : params.get('direction')
  const selected = ['sent', 'received'].includes(direction)
  const view = direction === 'received' ? params.get('view') : null
  const showRows = direction === 'sent' || (direction === 'received' && ['progress', 'history'].includes(view))
  const [rows, setRows] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!showRows) return
    let active = true
    setLoading(true); setRows([]); setError('')
    escrows.list(direction, view).then((data) => { if (active) setRows(data.escrows) })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [direction, view, showRows])

  if (!received && direction === 'received') {
    return <Navigate to={`/escrows/received${view ? `?view=${encodeURIComponent(view)}` : ''}`} replace />
  }

  return (
    <Card>
      <div className="mb-5 flex items-center justify-between">
        <h1 className="text-xl font-bold">{received ? 'Received money' : 'Escrows'}</h1>
      </div>
      {!received && <div className="grid gap-3 sm:grid-cols-2" aria-label="Escrow direction">
        {[['sent', 'Sent money', 'Payments you sent to sellers', '↗'],
          ['received', 'Received money', 'Payments sent to you', '↙']].map(([value, label, description, icon]) => (
          <button type="button" key={value} aria-pressed={direction === value}
            onClick={() => value === 'received' ? navigate('/escrows/received') : setParams({ direction: value })}
            className={`rounded-xl border p-4 text-left transition focus-visible:outline focus-visible:outline-teal-400 ${direction === value ? 'border-teal-400/50 bg-teal-400/10' : 'border-white/10 bg-navy-900/40 hover:border-teal-400/30'}`}>
            <span className="flex items-center justify-between font-semibold text-teal-300">
              {label}<span aria-hidden="true">{icon}</span>
            </span>
            <span className="mt-2 block text-xs text-slate-400">{description}</span>
          </button>
        ))}
      </div>}
      {direction === 'received' && <div className="mt-5 grid gap-3 sm:grid-cols-2" aria-label="Received money status">
        {[
          ['progress', 'In progress', 'Pending, held, or disputed payments'],
          ['history', 'History / Done', 'Released, refunded, or cancelled payments'],
        ].map(([value, label, description]) => <button key={value} type="button"
          aria-pressed={view === value} onClick={() => setParams({ view: value })}
          className={`rounded-xl border px-4 py-4 text-left transition focus-visible:outline focus-visible:outline-teal-400 ${view === value ? 'border-teal-400/50 bg-teal-400/10' : 'border-white/10 bg-navy-900/40 hover:border-teal-400/30'}`}>
          <span className="block text-sm font-semibold text-teal-300">{label}</span>
          <span className="mt-1 block text-xs text-slate-400">{description}</span>
        </button>)}
      </div>}
      {showRows ? <section className="mt-6" aria-live="polite" aria-busy={loading}>
        <h2 className="mb-3 font-semibold">{direction === 'sent' ? 'Sent money' : view === 'progress' ? 'Received money · In progress' : 'Received money · History / Done'}</h2>
        <Alert>{error}</Alert>
        {loading && <p className="text-sm text-slate-400">Loading escrows…</p>}
        {!loading && !error && rows.length === 0 && <p className="text-sm text-slate-400">
          {direction === 'sent' ? 'No sent escrows yet.' : view === 'progress' ? 'No received payments in progress.' : 'No received payment history yet.'}
        </p>}
        <ul className="divide-y divide-white/10">
          {rows.map((entry) => <EscrowRow key={entry.id} escrow={entry}
            onUpdate={(updated) => setRows((current) => current.map((row) => row.id === updated.id ? updated : row).filter((row) => direction !== 'received' || (view === 'history' ? ['released', 'refunded', 'cancelled'].includes(row.status) : ['hold', 'funded', 'disputed'].includes(row.status))))} />)}
        </ul>
      </section> : <p className="mt-5 text-sm text-slate-400">{selected ? 'Choose In progress or History / Done to view received money.' : 'Choose sent or received money to view your escrows.'}</p>}
    </Card>
  )
}
