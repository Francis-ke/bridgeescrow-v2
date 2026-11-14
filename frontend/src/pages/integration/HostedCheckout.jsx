import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { checkoutApi } from '../../api/integrations'
import { Alert } from '../../components/ui'
import CardEntry from '../../components/CardEntry'
import CheckoutBill from '../../components/integration/CheckoutBill'
import BuyerVerification from '../../components/integration/BuyerVerification'
import CheckoutReceipt from '../../components/integration/CheckoutReceipt'
import LivePayment from '../../components/integration/LivePayment'
import SandboxPayment from '../../components/integration/SandboxPayment'
export default function HostedCheckout() {
  const { token } = useParams()
  const [order, setOrder] = useState(null)
  const [session, setSession] = useState('')
  const [error, setError] = useState('')
  useEffect(() => {
    let active = true
    setOrder(null); setSession(''); setError('')
    checkoutApi(token).then((data) => { if (active) setOrder(data.order) })
      .catch((err) => { if (active) setError(err.message) })
    return () => { active = false }
  }, [token])
  async function verified(value) {
    const data = await checkoutApi(token, '', undefined, value)
    setSession(value); setOrder(data.order)
  }
  async function pay(data) {
    const result = await checkoutApi(token, 'pay', ['sandbox', 'production'].includes(order.environment) ? data : { last4: data.last4 }, session)
    await refresh()
    window.dispatchEvent(new Event('account-updated'))
    return result
  }
  async function refresh() {
    const result = await checkoutApi(token, '', undefined, session)
    setOrder(result.order)
  }
  return <div className="mx-auto max-w-lg space-y-5">
    <Alert>{error}</Alert>
    {!order && !error && <p>Loading checkout…</p>}
    {order && <>
      <CheckoutBill order={order} />
      {!session ? <BuyerVerification token={token} onVerified={verified} />
        : order.state === 'pending' ? <>
          <p className="text-sm text-teal-300">Email verified. Confirm the total and choose your payment method.</p>
          {order.environment === 'production' ? <LivePayment order={order} onPay={pay} onRefresh={refresh} /> : order.environment === 'sandbox' ? <SandboxPayment order={order} onPay={pay}
            onFailure={(body) => checkoutApi(token, 'sandbox-failure', body, session)} />
            : <CardEntry kind="checkout" fixedAmount={order.amount} onComplete={pay} />}
        </> : <CheckoutReceipt order={order} token={token} session={session} onRefresh={refresh} />}
    </>}
  </div>
}
