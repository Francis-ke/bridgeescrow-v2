import { useEffect, useState } from 'react'
import { phoneApi } from '../api/phone'
import { Alert } from '../components/ui'
import PhoneVerification from '../components/phone/PhoneVerification'
import SmsInbox from '../components/phone/SmsInbox'
import UssdSimulator from '../components/phone/UssdSimulator'
export default function PhoneChannels() {
  const [status, setStatus] = useState(null)
  const [refresh, setRefresh] = useState(0)
  const [error, setError] = useState('')
  const changed = () => setRefresh((value) => value + 1)
  useEffect(() => { phoneApi.status().then(setStatus).catch((err) => setError(err.message)) }, [])
  return <div className="space-y-6">
    <header><h1 className="text-2xl font-semibold">Phone & USSD</h1>
      <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-400">Connect one verified phone number to your BridgeEscrow account. Keep email login, sign in by phone, receive transaction messages and access your wallet over USSD.</p>
      {status && <p className="mt-3 text-xs text-amber-200">SMS: {status.sms_mode} · Payments: {status.payment_mode}</p>}</header>
    <Alert>{error}</Alert>
    <div className="grid items-start gap-6 lg:grid-cols-2">
      <div className="space-y-6"><PhoneVerification onChange={changed} /><UssdSimulator serviceCode={status?.ussd_service_code} onChange={changed} /></div>
      <SmsInbox refresh={refresh} />
    </div>
  </div>
}
