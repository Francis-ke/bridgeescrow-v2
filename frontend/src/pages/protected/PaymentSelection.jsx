import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { protectedPayments as api } from '../../api/protected'
import { Alert } from '../../components/ui'

const icons = { delivery: '↗', services: '◇', events: '✧', deposits: '↓',
  contracts: '≡', freelancing: '⌘', booking: '▦', other: '＋' }
export default function PaymentSelection() {
  const [categories, setCategories] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { api.categories().then((d) => setCategories(d.categories)).catch((e) => setError(e.message)) }, [])
  return <div className="space-y-6">
    <div><h1 className="text-2xl font-semibold">Hold-Escro protected payments</h1>
      <p className="mt-2 text-sm text-slate-400">Choose a payment type. Both parties agree to the terms before money is secured.</p></div>
    <Alert>{error}</Alert>
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{categories.map((category) => <Link
      to={`/protected/new/${category.id}`} key={category.id}
      className="rounded-2xl border border-white/10 bg-navy-800 p-5 transition hover:border-teal-400/50 focus-visible:outline focus-visible:outline-teal-400">
      <span aria-hidden="true" className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-teal-400/10 text-xl text-teal-300">{icons[category.id]}</span>
      <h2 className="font-semibold">{category.label}</h2>
      <p className="mt-2 text-xs leading-relaxed text-slate-400">{category.id === 'booking'
        ? 'Reserve a provider with agreed dates and cancellation rules.' : category.id === 'freelancing'
          ? 'Agree on work, milestones, revisions, and approval.' : 'Set clear deadlines, release rules, and cancellation terms.'}</p>
    </Link>)}</div>
    {!categories.length && !error && <p role="status">Loading payment categories…</p>}
  </div>
}
