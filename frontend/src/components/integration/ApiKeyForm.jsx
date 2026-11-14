import { useState } from 'react'
import { Button, Field } from '../ui'
export default function ApiKeyForm({ initial, email, onCreate, busy }) {
  const [form, setForm] = useState(initial || { business_name: '', website: '', contact_email: email || '', key_name: 'Website' })
  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value })
  return <form onSubmit={(e) => { e.preventDefault(); onCreate(form) }} className="space-y-4">
    <h2 className="text-lg font-semibold">Create your seller API</h2>
    <Field label="Business name" value={form.business_name} onChange={set('business_name')} minLength={3} maxLength={140} required />
    <Field label="Website URL" type="url" value={form.website} onChange={set('website')} placeholder="https://your-shop.com" required />
    <Field label="Business contact email" type="email" value={form.contact_email} onChange={set('contact_email')} required />
    <Field label="Key name" value={form.key_name || 'Website'} onChange={set('key_name')} required />
    <Button type="submit" disabled={busy}>{busy ? 'Creating…' : 'Create API key'}</Button>
  </form>
}
