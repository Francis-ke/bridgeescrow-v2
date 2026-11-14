import { useEffect, useRef, useState } from 'react'
import { phoneApi } from '../api/phone'
import ProviderDeposit from './phone/ProviderDeposit'
import ProviderPayout from './phone/ProviderPayout'
import CardEntry from './CardEntry'
import MpesaMethod from './MpesaMethod'
import TransactionReceipt from './TransactionReceipt'
import { payments } from '../api/endpoints'
import { checkoutPayload } from '../api/demoCheckout'

export default function PaymentMethods({ title, kind, allowMpesa = false }) {
  const [channel, setChannel] = useState(null)
  const [channelError, setChannelError] = useState('')
  useEffect(() => { phoneApi.status().then(setChannel).catch((err) => setChannelError(err.message)) }, [])
  const [method, setMethod] = useState('card')
  const [receipt, setReceipt] = useState(null)
  const requestKey = useRef(null)
  async function complete(data) {
    const signature = JSON.stringify({ ...data, kind })
    if (!requestKey.current || requestKey.current.signature !== signature) {
      requestKey.current = { signature, key: crypto.randomUUID() }
    }
    const result = await payments.demoCheckout(checkoutPayload({ ...data, kind }, requestKey.current.key))
    setReceipt(result.receipt)
    window.dispatchEvent(new Event('account-updated'))
  }
  if (!channel) return <p role="status" className="text-sm text-slate-400">{channelError || 'Loading payment configuration…'}</p>
  if (channel.payment_mode !== 'simulated' && kind === 'deposit') return <ProviderDeposit mode={channel.payment_mode} />
  if (channel.payment_mode !== 'simulated' && kind === 'withdraw') return <ProviderPayout mode={channel.payment_mode} />
  if (receipt) return <div className="mx-auto max-w-lg"><TransactionReceipt title={title} receipt={receipt} onAgain={() => { requestKey.current = null; setReceipt(null) }} /></div>
  return (
    <div className="mx-auto max-w-lg space-y-5">
      <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
      {channel.payment_mode === 'simulated' && kind !== 'send' && <details className="text-xs text-slate-500"><summary className="cursor-pointer">Payment environment</summary><p className="mt-2">Payments in this environment are simulated. No bank card is charged and no real M-PESA transfer is made.</p></details>}
      {kind === 'send' && <p className="text-sm text-slate-400">Money goes directly from your wallet to the receiving account. The full amount is available immediately.</p>}
      {allowMpesa && <div className="grid grid-cols-2 gap-2 rounded-xl border border-white/10 bg-navy-800/70 p-1.5" aria-label="Payment method">
        {[['card', 'Card'], ['mpesa', 'M-PESA']].map(([value, label]) => <button key={value} type="button"
          aria-pressed={method === value} onClick={() => setMethod(value)}
          className={`rounded-lg px-4 py-3 text-sm font-semibold transition focus-visible:outline focus-visible:outline-teal-400 ${method === value ? 'bg-teal-400 text-navy-900 shadow-sm' : 'text-slate-400 hover:text-white'}`}>
          {label}
        </button>)}
      </div>}
      {method === 'card' ? <CardEntry kind={kind} onComplete={complete} />
        : <MpesaMethod kind={kind} onComplete={complete} />}
    </div>
  )
}
