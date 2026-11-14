import HoldDecision from '../components/HoldDecision'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { escrows } from '../api/endpoints'
import { Alert, Card } from '../components/ui'
import EscrowActions from '../components/EscrowActions'
import ContractPanel from '../components/ContractPanel'
import DisputePanel from '../components/DisputePanel'
import TransactionDetails from '../components/TransactionDetails'
import ReceiptHoldForm from '../components/ReceiptHoldForm'
import ProtectedDetail from './protected/ProtectedDetail'

export default function EscrowDetail() {
  const { id } = useParams()
  const [escrow, setEscrow] = useState(null)
  const [error, setError] = useState('')

  const load = () => escrows.one(id).then((d) => setEscrow(d.escrow))
    .catch((e) => setError(e.message))
  useEffect(() => { load() }, [id])

  if (error) return <Alert>{error}</Alert>
  if (!escrow) return <p className="text-slate-400">Loading…</p>

  if (escrow.protection) return <ProtectedDetail id={id} />

  return (
    <div className="mx-auto max-w-lg space-y-4">
      <Card>
        <p className="text-xs uppercase text-slate-500">{escrow.reference}</p>
        <h1 className="text-xl font-bold">{escrow.title}</h1>
        <p className="mt-2 text-2xl font-bold text-teal-400">KES {escrow.amount}</p>
        <p className="text-xs text-slate-500">
          Fee {escrow.fee} · Status <span className="uppercase">{escrow.status}</span>
        </p>
        <div className="mt-5 border-t border-white/10 pt-4">
          <TransactionDetails escrow={escrow} />
        </div>
        <ReceiptHoldForm escrow={escrow} onUpdate={setEscrow} />
        <HoldDecision escrow={escrow} onUpdate={setEscrow} />
        <EscrowActions escrow={escrow} reload={load} />
        <ContractPanel escrowId={escrow.id} status={escrow.status} />
        <DisputePanel escrow={escrow} reload={load} />
      </Card>
    </div>
  )
}
