import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { protectedPayments as api } from '../../api/protected'
import { Alert, Card } from '../../components/ui'
import ProtectedSummary from '../../components/protected/ProtectedSummary'
import ProtectedControls from '../../components/protected/ProtectedControls'
import WorkMilestone from '../../components/protected/WorkMilestone'
import TransactionDetails from '../../components/TransactionDetails'
import { dateTime } from '../../components/protected/format'
export default function ProtectedDetail({ id, admin = false }) {
  const location = useLocation()
  const [payment, setPayment] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    ;(admin ? api.adminDetail(id) : api.detail(id)).then((data) => { if (active) setPayment(data.payment) })
      .catch((err) => { if (active) setError(err.message) })
    return () => { active = false }
  }, [id, admin, location.key])
  async function act(action, body = {}) {
    if (busy) return false
    setBusy(true); setError('')
    try {
      const data = await api.act(id, action, body)
      setPayment(data.payment); window.dispatchEvent(new Event('account-updated'))
      return true
    } catch (err) { setError(err.message); return false } finally { setBusy(false) }
  }
  if (!payment) return <><Alert>{error}</Alert>{!error && <p>Loading protected payment…</p>}</>
  return <div className="mx-auto max-w-3xl space-y-5" aria-busy={busy}>
    <Alert>{error}</Alert>
    <Card><ProtectedSummary payment={payment} /></Card>
    <Card><TransactionDetails escrow={payment.escrow} /></Card>
    {payment.category !== 'booking' && <Card><h2 className="mb-4 text-lg font-semibold">Work and milestones</h2>
      <div className="space-y-4">{payment.milestones.map((item, index) => <WorkMilestone key={item.id} item={item}
        payment={payment} onAction={act} busy={busy} ready={payment.milestones.slice(0, index).every((row) => row.state === 'approved')} />)}</div>
    </Card>}
    <Card><ProtectedControls payment={payment} onAction={act} busy={busy} /></Card>
    <Card><h2 className="mb-3 font-semibold">Payment activity</h2><ol className="divide-y divide-white/10">{payment.events.map((row, i) => <li key={i} className="py-3 text-sm">
      <p className="capitalize text-teal-300">{row.action.replaceAll('_', ' ')}</p>
      <p className="break-words text-slate-400">{row.detail}</p><time className="text-xs text-slate-500">{dateTime(row.at)}</time>
    </li>)}</ol></Card>
  </div>
}
