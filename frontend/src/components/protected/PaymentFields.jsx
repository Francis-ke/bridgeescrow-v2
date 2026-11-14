import { Field } from '../ui'
export default function PaymentFields({ category, form, setForm, providers }) {
  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value })
  return <>
    <label className="block text-sm text-slate-300">{category === 'freelancing' ? 'Freelancer' : 'Provider'}
      <select required value={form.provider_id} onChange={set('provider_id')}
        className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2">
        <option value="">Choose a registered provider</option>
        {providers.map((p) => <option key={p.id} value={p.id}>{p.name} · {p.email}</option>)}
      </select>
    </label>
    <Field label="Title" minLength={3} maxLength={140} required value={form.title} onChange={set('title')} />
    <label className="block text-sm text-slate-300">{category === 'freelancing' ? 'Job description and deliverables' : 'Service description and agreed terms'}
      <textarea required minLength={20} maxLength={10000} rows={4} value={form.description} onChange={set('description')}
        className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2" />
    </label>
    <Field label="Total amount (KES)" type="number" min="10" step="0.01" required value={form.amount} onChange={set('amount')} />
    {category === 'booking' && <div className="grid gap-3 sm:grid-cols-2">
      <Field label="Booking starts" type="datetime-local" required value={form.booking_start} onChange={set('booking_start')} />
      <Field label="Booking ends" type="datetime-local" required value={form.booking_end} onChange={set('booking_end')} />
    </div>}
    <Field label="Completion deadline" type="datetime-local" required value={form.deadline} onChange={set('deadline')} />
  </>
}
