import { get, post, request } from './client'
export const phoneApi = {
  status: () => get('/phone/status'),
  start: (phone) => post('/phone/verification', { phone }),
  verify: (challenge_id, otp) => post('/phone/verify', { challenge_id, otp }),
  messages: () => get('/phone/messages'),
  testSms: () => post('/phone/sms-test', {}),
  dial: (session_id, text) => post('/ussd/simulate', { session_id, text }),
  deposit: (amount, key) => request('/payments/stk-push', { method: 'POST',
    headers: { 'Idempotency-Key': key }, body: { amount } }),
}
