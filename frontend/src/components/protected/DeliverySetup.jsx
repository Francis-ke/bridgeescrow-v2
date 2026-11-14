import { Button, Field } from '../ui'
export default function DeliverySetup({ form, setForm, onContinue }) {
  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value })
  return <form onSubmit={(event) => { event.preventDefault(); onContinue() }} className="space-y-5">
    <div className="grid grid-cols-2 gap-3">
      <Field label="Time duration" type="number" min="1" max={form.unit === 'days' ? 90 : 2160}
        step="1" required value={form.duration} onChange={set('duration')} />
      <label className="block text-sm text-slate-300">Time unit
        <select value={form.unit} onChange={set('unit')}
          className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2">
          <option value="hours">Hours</option><option value="days">Days</option>
        </select>
      </label>
    </div>
    <Field label="Amount (KES)" type="number" min="10" max="5000000" step="0.01"
      required value={form.amount} onChange={set('amount')} />
    <Button type="submit" className="w-full">Continue</Button>
  </form>
}
