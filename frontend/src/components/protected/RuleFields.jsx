import { Field } from '../ui'
export default function RuleFields({ category, rules, setRules }) {
  const set = (key, numeric = false) => (event) => setRules({ ...rules,
    [key]: numeric ? Number(event.target.value) : event.target.value })
  return <details open className="rounded-xl border border-white/10 p-4">
    <summary className="cursor-pointer font-medium text-teal-300">Release, extension and cancellation rules</summary>
    <div className="mt-4 space-y-4">
      <label className="block text-sm text-slate-300">Release rule
        <select value={rules.release || 'client_approval'} onChange={set('release')}
          className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 px-3 py-2">
          <option value="client_approval">Client approval / attendance confirmation</option>
          <option value="mutual_confirmation">Both parties confirm completion</option>
        </select>
      </label>
      <Field label="Cancellation deadline" type="datetime-local" required value={rules.cancellation_deadline || ''} onChange={set('cancellation_deadline')} />
      <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Refund before deadline (%)" type="number" min="0" max="100" required value={rules.early_refund_percent ?? 100} onChange={set('early_refund_percent', true)} />
        <Field label="Refund after deadline (%)" type="number" min="0" max="100" required value={rules.late_refund_percent ?? 0} onChange={set('late_refund_percent', true)} />
      </div>
      <p className="text-xs text-slate-400">{category === 'booking'
        ? 'These booking-specific percentages apply to the remaining secured funds. Provider cancellation refunds 100%. No general 80/20 policy is applied.'
        : 'Funded cancellation requires the other party’s approval. Percentages apply only to remaining funds.'}</p>
      <Field label="Maximum extension (hours)" type="number" min="1" max="2160" required value={rules.max_extension_hours ?? 168} onChange={set('max_extension_hours', true)} />
      {category !== 'booking' && <div className="grid gap-3 sm:grid-cols-2">
        <Field label="Maximum revisions" type="number" min="0" max="20" value={rules.max_revisions ?? 3} onChange={set('max_revisions', true)} />
        <Field label="Time per revision (hours)" type="number" min="1" max="720" value={rules.revision_hours ?? 48} onChange={set('revision_hours', true)} />
      </div>}
      <p className="text-xs text-slate-500">Both parties accept these rules before funding. The provider pays a 1% platform fee on released funds.</p>
    </div>
  </details>
}
