import test from 'node:test'
import assert from 'node:assert/strict'
import { checkoutPayload } from './demoCheckout.js'

test('checkout requests never include funding-card numbers, expiry, or CVV', () => {
  const payload = checkoutPayload({ kind: 'deposit', method: 'card', amount: '100',
    number: '9900123456789012', expiry: '12/29', cvv: '123', last4: '9012' }, 'test-request-key')
  for (const key of ['number', 'expiry', 'cvv', 'recipient_card']) assert.ok(!(key in payload))
  assert.equal(payload.last4, '9012')
  assert.equal(payload.idempotency_key, 'test-request-key')
})

test('send requests identify the receiving virtual account and preserve retry keys', () => {
  const data = { kind: 'send', method: 'card', amount: '50', recipient_card: '9900123456789012' }
  const first = checkoutPayload(data, 'same-request-key')
  assert.deepEqual(first, checkoutPayload(data, 'same-request-key'))
  assert.equal(first.recipient_card, data.recipient_card)
})
