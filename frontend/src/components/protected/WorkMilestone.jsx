import { useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { Button } from '../ui'
import ReasonAction from './ReasonAction'
import { dateTime, money } from './format'
export default function WorkMilestone({ item, payment, onAction, busy, ready }) {
  const [submission, setSubmission] = useState('')
  const { user } = useAuth()
  const client = user.id === payment.escrow.transaction.sender.id
  async function send(event) {
    event.preventDefault()
    if (await onAction('submit', { milestone_id: item.id, submission })) setSubmission('')
  }
  return <article className="space-y-3 rounded-xl border border-white/10 bg-navy-900/50 p-4">
    <div className="flex flex-wrap justify-between gap-2"><h3 className="font-semibold">{item.title}</h3><span>{money(item.amount)}</span></div>
    <p className="text-xs text-slate-400">{item.state.replaceAll('_', ' ')} · Due {dateTime(item.revision_due || item.deadline)}</p>
    {item.submission && <div className="whitespace-pre-wrap break-words rounded-lg bg-white/5 p-3 text-sm"><p className="mb-1 text-xs text-teal-300">Work submission</p>{item.submission}</div>}
    {item.revision_reason && <p className="text-sm text-amber-300">Revision {item.revision_count}: {item.revision_reason}</p>}
    {!client && ready && ['pending', 'revision_requested'].includes(item.state) && payment.actions.includes('submit') && <form onSubmit={send} className="space-y-2">
      <label className="block text-sm">Work details or delivery link
        <textarea required minLength={10} maxLength={10000} rows={3} value={submission} onChange={(event) => setSubmission(event.target.value)}
          className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 p-3" /></label>
      <Button disabled={busy} type="submit">Submit work</Button>
    </form>}
    {client && ready && item.state === 'submitted' && payment.actions.includes('approve') && <>
      <Button disabled={busy} onClick={() => onAction('approve', { milestone_id: item.id })}>Approve and release {money(item.amount)}</Button>
      {item.revision_count < payment.rules.max_revisions && <ReasonAction action="revise" title="Request revisions" onAction={onAction} busy={busy} extra={{ milestone_id: item.id }} />}
    </>}
  </article>
}
