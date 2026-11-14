import { useState } from 'react'
import { Button, Field } from '../ui'
export default function ApplicationForm({ application, onSave, busy, allowProduction = false }) {
  const [form, setForm] = useState({ name: application?.name || '', description: application?.description || '',
    website: application?.website || '', type: application?.type || 'website', environment: application?.environment || 'sandbox' })
  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value })
  async function submit(event) {
    event.preventDefault()
    if (await onSave(form) && !application) setForm({ name: '', description: '', website: '', type: 'website', environment: 'sandbox' })
  }
  return <form onSubmit={submit} className="space-y-4">
    <Field label="Application name" required minLength={3} maxLength={100} value={form.name} onChange={set('name')} />
    <label className="block text-sm text-slate-300">Application description
      <textarea required minLength={10} maxLength={2000} rows={3} value={form.description} onChange={set('description')}
        className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 p-3" />
    </label>
    <Field label="Website URL (optional)" type="url" placeholder="https://your-store.example" value={form.website} onChange={set('website')} />
    <div className="grid gap-4 sm:grid-cols-2">
      <label className="block text-sm text-slate-300">Application type
        <select value={form.type} onChange={set('type')} className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 p-2.5">
          <option value="website">Website</option><option value="mobile">Mobile</option><option value="backend">Backend</option>
        </select>
      </label>
      {allowProduction && !application ? <label className="block text-sm text-slate-300">Environment
        <select value={form.environment} onChange={set('environment')} className="mt-1 w-full rounded-lg border border-white/10 bg-navy-900 p-2.5"><option value="sandbox">Sandbox</option><option value="production">Production · live M-PESA</option></select>
      </label> : <Field label="Environment" readOnly value={form.environment === 'production' ? 'Production' : 'Sandbox'} />}
    </div>
    <Button type="submit" disabled={busy}>{busy ? 'Saving…' : application ? 'Save settings' : 'Create application'}</Button>
  </form>
}
