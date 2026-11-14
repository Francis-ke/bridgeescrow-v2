import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { protectedPayments as api } from '../../api/protected'
import { Alert, Button, Card } from '../../components/ui'
import PaymentFields from '../../components/protected/PaymentFields'
import RuleFields from '../../components/protected/RuleFields'
import MilestoneEditor from '../../components/protected/MilestoneEditor'
import DeliveryNew from './DeliveryNew'
import { createPayload, initialForm, localDate } from '../../components/protected/formValues'

function AdvancedProtectedNew() {
  const { category } = useParams()
  const [form, setForm] = useState(initialForm)
  const [rules, setRules] = useState({})
  const [milestones, setMilestones] = useState([])
  const [providers, setProviders] = useState([])
  const [label, setLabel] = useState('Protected payment')
  const [busy, setBusy] = useState(false)
  const [ready, setReady] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  useEffect(() => {
    setReady(false); setForm(initialForm()); setMilestones([]); setError('')
    let active = true
    Promise.all([api.categories(), api.providers()]).then(([types, people]) => {
      if (!active) return
      const selected = types.categories.find((item) => item.id === category)
      if (!selected) throw new Error('Unknown payment category')
      setRules({ ...selected.defaults, cancellation_deadline: localDate(24) })
      setLabel(selected.label); setProviders(people.providers); setReady(true)
    }).catch((err) => { if (active) setError(err.message) })
    return () => { active = false }
  }, [category])
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      const result = await api.create(createPayload(category, form, rules, milestones))
      navigate(`/escrows/${result.payment.escrow.id}`)
    } catch (err) { setError(err.message) } finally { setBusy(false) }
  }
  return <div className="mx-auto max-w-2xl"><Card>
    <h1 className="mb-2 text-2xl font-semibold">{label}</h1>
    <p className="mb-6 text-sm text-slate-400">Agree on the work, dates, release and cancellation rules before funding.</p>
    <Alert>{error}</Alert>
    {ready && <form onSubmit={submit} className="mt-4 space-y-5">
      <PaymentFields category={category} form={form} setForm={setForm} providers={providers} />
      <RuleFields category={category} rules={rules} setRules={setRules} />
      {category === 'freelancing' && <MilestoneEditor items={milestones} setItems={setMilestones} />}
      <Button type="submit" disabled={busy || !providers.length}>{busy ? 'Creating…' : 'Create protected payment'}</Button>
      {!providers.length && <p className="text-sm text-slate-400">Another verified account is needed as the provider.</p>}
    </form>}
  </Card></div>
}

export default function ProtectedNew() {
  const { category } = useParams()
  return category === 'delivery' ? <DeliveryNew /> : <AdvancedProtectedNew />
}
