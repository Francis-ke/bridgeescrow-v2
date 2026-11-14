import { get, post, request } from './client'
export const sellerApi = {
  settings: () => get('/seller/api'),
  createKey: (body) => post('/seller/api/keys', body),
  revoke: (id) => request(`/seller/api/keys/${id}`, { method: 'DELETE' }),
  orders: () => get('/seller/orders'),
  createOrder: (body) => post('/seller/orders', body),
  redeem: (id, code) => post(`/seller/orders/${id}/redeem`, { code }),
}
export async function checkoutApi(token, action = '', body, session) {
  const response = await fetch(`/api/checkout/${encodeURIComponent(token)}${action ? '/' + action : ''}`, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json', ...(session ? { 'X-Checkout-Session': session } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const data = await response.json()
  if (!response.ok) throw new Error(data.error?.message || 'Checkout request failed')
  return data
}
