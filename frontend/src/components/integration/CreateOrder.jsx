import { useState } from 'react'
import { Button, Field } from '../ui'
export default function CreateOrder({ onCreate, busy }) {
  const [form, setForm] = useState({ order_id: '', description: '', amount: '' })
  const set = (key) => (event) => setForm({ ...form, [key]: event.target.value })
  return <form onSubmit={(e) => { e.preventDefault(); onCreate({ order_id: form.order_id,
    items: [{ description: form.description, quantity: 1, unit_amount: form.amount }] }) }} className="space-y-3">
    <h2 className="text-lg font-semibold">Create a checkout link</h2>
    <Field label="Shop order reference" required value={form.order_id} onChange={set('order_id')} />
    <Field label="Item or package" required value={form.description} onChange={set('description')} />
    <Field label="Bill total (KES)" type="number" min="10" step="0.01" required value={form.amount} onChange={set('amount')} />
    <Button type="submit" disabled={busy}>Create checkout link</Button>
  </form>
}
