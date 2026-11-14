import { Button } from '../ui'
import ExtensionControls from './ExtensionControls'
import ReasonAction from './ReasonAction'
export default function ProtectedControls({ payment: p, onAction, busy }) {
  return <section className="space-y-4 border-t border-white/10 pt-5">
    <div className="flex flex-wrap gap-3">
      {p.actions.includes('accept') && <Button disabled={busy} onClick={() => onAction('accept')}>Accept terms {p.category === 'booking' ? 'and reservation' : ''}</Button>}
      {p.actions.includes('fund') && <Button disabled={busy} onClick={() => onAction('fund')}>Secure KES {p.escrow.amount} from wallet</Button>}
      {p.actions.includes('confirm') && <Button disabled={busy} onClick={() => onAction('confirm')}>Confirm service / attendance</Button>}
    </div>
    <ExtensionControls payment={p} onAction={onAction} busy={busy} />
    {p.cancellation && <p className="text-sm text-slate-400">Cancellation {p.cancellation.status} · {p.cancellation.refund_percent}% refund · {p.cancellation.reason}</p>}
    {p.actions.includes('cancel') && <ReasonAction action="cancel" title={p.category === 'booking' ? 'Cancel booking' : 'Request cancellation'} onAction={onAction} busy={busy} />}
    {p.actions.includes('decide-cancel') && <div className="flex gap-3">
      <Button disabled={busy} onClick={() => onAction('decide-cancel', { decision: 'accept' })}>Accept cancellation</Button>
      <Button variant="ghost" disabled={busy} onClick={() => onAction('decide-cancel', { decision: 'decline' })}>Decline cancellation</Button>
    </div>}
    {p.actions.includes('dispute') && <ReasonAction action="dispute" title="Open dispute" onAction={onAction} busy={busy} />}
  </section>
}
