import PaymentMethods from '../components/PaymentMethods'
import PaymentSelection from './protected/PaymentSelection'

export default function PaymentAction({ mode }) {
  if (mode === 'buy') return <PaymentSelection />
  return <PaymentMethods title="Send money" kind="send" />
}
