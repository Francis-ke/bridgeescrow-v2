import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { protectedPayments as api } from '../../api/protected'
import { Card } from '../../components/ui'
import CardEntry from '../../components/CardEntry'
import DeliverySetup from '../../components/protected/DeliverySetup'

export default function DeliveryNew() {
  const [form, setForm] = useState({ duration: '24', unit: 'hours', amount: '' })
  const [step, setStep] = useState(1)
  const navigate = useNavigate()
  async function confirm(data) {
    const result = await api.createDelivery({ recipient_card: data.recipient_card,
      account_holder: data.destination, amount: form.amount,
      duration_hours: Number(form.duration) * (form.unit === 'days' ? 24 : 1) })
    navigate(`/escrows/${result.payment.escrow.id}`)
  }
  return <div className="mx-auto max-w-lg space-y-4">
    {step === 1 ? <Card>
      <h1 className="mb-6 text-2xl font-semibold">Delivery</h1>
      <DeliverySetup form={form} setForm={setForm} onContinue={() => setStep(2)} />
    </Card> : <>
      <CardEntry kind="delivery" receivingAccount fixedAmount={form.amount} onComplete={confirm} />
      <button type="button" onClick={() => setStep(1)} className="text-sm text-teal-300">Edit duration and amount</button>
    </>}
  </div>
}
