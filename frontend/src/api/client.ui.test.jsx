import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import { request } from './client'

beforeEach(() => {
  const values = new Map()
  vi.stubGlobal('localStorage', {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
  })
})
afterEach(() => { vi.unstubAllGlobals() })
const reply = (status, data) => ({ ok: status < 400, status,
  text: async () => JSON.stringify(data) })

test('expired authentication clears only the session used by the request', async () => {
  localStorage.setItem('be_token', 'expired-token')
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reply(401, {
    error: { code: 'token_expired', message: 'Session expired' },
  })))
  const expired = vi.fn()
  window.addEventListener('session-expired', expired)
  try {
    await expect(request('/wallet')).rejects.toMatchObject({ status: 401 })
    expect(expired).toHaveBeenCalledTimes(1)
  } finally { window.removeEventListener('session-expired', expired) }
})

test('a late failure from an old account does not expire a new login', async () => {
  localStorage.setItem('be_token', 'old-token')
  let finish
  vi.stubGlobal('fetch', vi.fn(() => new Promise((resolve) => { finish = resolve })))
  const expired = vi.fn()
  window.addEventListener('session-expired', expired)
  try {
    const pending = request('/wallet')
    localStorage.setItem('be_token', 'new-token')
    finish(reply(401, { error: { code: 'token_expired' } }))
    await expect(pending).rejects.toMatchObject({ status: 401 })
    expect(expired).not.toHaveBeenCalled()
  } finally { window.removeEventListener('session-expired', expired) }
})

test('successful writes refresh balances while failed writes do not', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(reply(200, {}))
    .mockResolvedValueOnce(reply(409, { error: { message: 'Insufficient funds' } })))
  const updated = vi.fn()
  window.addEventListener('account-updated', updated)
  try {
    await request('/wallet/withdraw', { method: 'POST', body: { amount: '10' } })
    await expect(request('/wallet/withdraw', { method: 'POST' })).rejects.toMatchObject({ status: 409 })
    expect(updated).toHaveBeenCalledTimes(1)
  } finally { window.removeEventListener('account-updated', updated) }
})
