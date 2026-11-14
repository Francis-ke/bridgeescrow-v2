import { get, post, put } from './client'

export const auth = {
  register: (d) => post('/auth/register', d),
  verifyRegistration: (d) => post('/auth/register/verify', d),
  resendRegistration: (email) => post('/auth/register/resend', { email }),
  login: (d) => post('/auth/login', d),
  me: () => get('/auth/me'),
  updateProfile: (data) => put('/auth/me', data),
  setPin: (pin) => post('/auth/pin', { pin }),
  forgotPassword: (email) => post('/auth/password/forgot', { email }),
  resetPassword: (d) => post('/auth/password/reset', d),
}

export const wallet = {
  get: () => get('/wallet'),
  ledger: () => get('/wallet/ledger'),
  deposit: (amount, idempotency_key) => post('/wallet/deposit', { amount, idempotency_key }),
  withdraw: (amount, pin) => post('/wallet/withdraw', { amount, pin }),
}

export const escrows = {
  list: (direction, view) => {
    const params = new URLSearchParams()
    if (direction) params.set('direction', direction)
    if (view) params.set('view', view)
    return get(`/escrows${params.size ? `?${params}` : ''}`)
  },
  create: (d) => post('/escrows', d),
  one: (id) => get(`/escrows/${id}`),
  fund: (id) => post(`/escrows/${id}/fund`),
  release: (id) => post(`/escrows/${id}/release`),
  confirm: (id, code) => post(`/escrows/${id}/confirm`, { code }),
  refund: (id) => post(`/escrows/${id}/refund`),
  decideHold: (id, decision) => post(`/escrows/${id}/receipt-hold/decision`, { decision }),
  receiptHold: (id, data) => put(`/escrows/${id}/receipt-hold`, data),
  cancel: (id) => post(`/escrows/${id}/cancel`),
  contract: (id) => get(`/escrows/${id}/contract`),
  saveContract: (id, d) => put(`/escrows/${id}/contract`, d),
  signContract: (id) => post(`/escrows/${id}/contract/sign`),
  dispute: (id, reason) => post(`/escrows/${id}/disputes`, { reason }),
  disputes: (id) => get(`/escrows/${id}/disputes`),
}

export const payments = {
  demoCheckout: (data) => post('/payments/demo-checkout', data),
  list: () => get('/payments'),
  stkPush: (amount, msisdn) => post('/payments/stk-push', { amount, msisdn }),
  simulate: (id) => post(`/payments/${id}/simulate`),
}

export const dashboard = { summary: () => get('/dashboard') }
export const analytics = { me: () => get('/analytics/me') }

export const notifications = {
  readAll: () => put('/notifications/read-all', {}),
  list: () => get('/notifications'),
  read: (id) => put(`/notifications/${id}/read`, {}),
}
