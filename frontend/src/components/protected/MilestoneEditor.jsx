import { Field, Button } from '../ui'
import { localDate } from './formValues'
export default function MilestoneEditor({ items, setItems }) {
  const edit = (index, key) => (event) => setItems(items.map((m, i) => i === index ? { ...m, [key]: event.target.value } : m))
  return <section className="space-y-3 rounded-xl border border-white/10 p-4">
    <h2 className="font-medium">Optional milestones</h2>
    <p className="text-xs text-slate-400">Amounts must equal the total. Milestones are paid individually after approval, in order.</p>
    {items.map((m, index) => <div key={index} className="space-y-3 rounded-lg bg-navy-900 p-3">
      <Field label={`Milestone ${index + 1} title`} required minLength={3} value={m.title} onChange={edit(index, 'title')} />
      <Field label="Milestone amount (KES)" required min="10" step="0.01" type="number" value={m.amount} onChange={edit(index, 'amount')} />
      <Field label="Milestone deadline" required type="datetime-local" value={m.deadline} onChange={edit(index, 'deadline')} />
      <Button type="button" variant="ghost" onClick={() => setItems(items.filter((_, i) => i !== index))}>Remove milestone</Button>
    </div>)}
    <Button type="button" variant="ghost" disabled={items.length >= 12}
      onClick={() => setItems([...items, { title: '', amount: '', deadline: localDate(120) }])}>Add milestone</Button>
  </section>
}
