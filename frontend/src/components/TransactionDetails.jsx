function dateTime(value) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  return new Intl.DateTimeFormat('en-KE', {
    dateStyle: 'medium', timeStyle: 'short', timeZone: 'Africa/Nairobi',
  }).format(date) + ' EAT'
}

function cardNumber(value) {
  return value ? value.replace(/(.{4})/g, '$1 ').trim() : 'Unavailable'
}

export default function TransactionDetails({ escrow }) {
  const transaction = escrow.transaction
  if (!transaction) return null
  const rows = [
    ['Amount', `${escrow.currency || 'KES'} ${Number(escrow.amount).toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`],
    ['From', transaction.sender?.name],
    ['Sender email', transaction.sender?.email],
    ['Sender card number', cardNumber(transaction.sender?.card_number)],
    ['To', transaction.recipient?.name],
    ['Recipient email', transaction.recipient?.email],
    ['Recipient card number', cardNumber(transaction.recipient?.card_number)],
    ['Payment method', 'Wallet'],
    ['Created', dateTime(transaction.transaction_at)],
    ['Money sent', dateTime(transaction.funded_at) || 'Not funded yet'],
    ['When to receive', dateTime(transaction.received_at) || transaction.receipt_status],
  ]
  if (transaction.hold_request?.status) {
    rows.push(['Hold-time request', `${transaction.hold_request.hours} hours — ${transaction.hold_request.status}`])
    rows.push(['Requested reason', transaction.hold_request.reason])
  }
  if (transaction.receipt_hold_until) {
    rows.push(['Hold until', dateTime(transaction.receipt_hold_until)])
    rows.push(['Hold reason', transaction.receipt_hold_reason])
  }
  if (transaction.expected_delivery_at && ['funded', 'disputed'].includes(escrow.status)) {
    rows.push(['Estimated delivery', dateTime(transaction.expected_delivery_at)])
  }

  return (
    <dl className="grid gap-x-5 gap-y-3 text-sm sm:grid-cols-2">
      {rows.map(([label, value]) => <div key={label} className="min-w-0">
        <dt className="text-xs text-slate-500">{label}</dt>
        <dd className="mt-1 break-words text-slate-300">{value || 'Unavailable'}</dd>
      </div>)}
    </dl>
  )
}
