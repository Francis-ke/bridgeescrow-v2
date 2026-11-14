import { useEffect, useState } from 'react'
import { protectedPayments as api } from '../../api/protected'
import { Alert, Card } from '../../components/ui'
import CategoryReport from '../../components/protected/CategoryReport'
import DisputeResolution from '../../components/protected/DisputeResolution'
import EscrowRow from '../../components/EscrowRow'
export default function Reports({ admin = false }) {
  const [data, setData] = useState(null)
  const [disputes, setDisputes] = useState([])
  const [error, setError] = useState('')
  async function load() {
    try {
      const [report, issues] = await Promise.all([admin ? api.admin() : api.reports(), admin ? api.disputes() : Promise.resolve({ disputes: [] })])
      setData(report); setDisputes(issues.disputes); setError('')
    } catch (err) { setError(err.message) }
  }
  useEffect(() => { load() }, [admin])
  return <div className="space-y-5">
    <h1 className="text-2xl font-semibold">{admin ? 'Administrator analytics and disputes' : 'Merchant payment report'}</h1>
    <Alert>{error}</Alert>
    {data && <Card><CategoryReport rows={data.protected_categories || []} /></Card>}
    {admin ? <div className="space-y-4">{disputes.filter((row) => row.status === 'open').map((row) => <DisputeResolution key={row.id} dispute={row} onDone={load} />)}</div>
      : data && <Card><h2 className="mb-3 font-semibold">Sales history</h2><ul>{data.sales.map((row) => <EscrowRow key={row.id} escrow={row} onUpdate={load} />)}</ul></Card>}
  </div>
}
