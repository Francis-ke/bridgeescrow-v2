export function checkoutPayload(data, idempotencyKey) {
  const payload = {
    kind: data.kind, method: data.method, amount: data.amount,
    destination: data.destination || '', last4: data.last4 || '',
    idempotency_key: idempotencyKey,
  }
  if (data.kind === 'send') payload.recipient_card = data.recipient_card || ''
  return payload
}
