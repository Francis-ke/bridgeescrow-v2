import { beforeEach, afterEach, expect, test, vi } from 'vitest'
import { act, render, screen } from '@testing-library/react'
import { AuthProvider, useAuth } from './AuthContext'
import { auth } from '../api/endpoints'
vi.mock('../api/endpoints', () => ({ auth: { me: vi.fn() } }))
beforeEach(() => {
  const values = new Map([['be_token', 'first-token']])
  vi.stubGlobal('localStorage', {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value), removeItem: (key) => values.delete(key),
  })
  auth.me.mockReset()
})
afterEach(() => vi.unstubAllGlobals())
function Consumer() {
  const { user, loading } = useAuth()
  return <p>{loading ? 'Loading account' : user?.full_name || 'Signed out'}</p>
}
const profile = (id, full_name) => ({ user: { id, full_name, card_number: '9900', card_cvv: '123' } })

test('switching account in another tab clears the old profile until the new one arrives', async () => {
  auth.me.mockResolvedValueOnce(profile(1, 'First User'))
  render(<AuthProvider><Consumer /></AuthProvider>)
  await screen.findByText('First User')
  let finish
  auth.me.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve }))
  act(() => {
    localStorage.setItem('be_token', 'second-token')
    window.dispatchEvent(new StorageEvent('storage', { key: 'be_token' }))
  })
  expect(screen.queryByText('First User')).toBeNull()
  expect(screen.getByText('Loading account')).toBeTruthy()
  await act(async () => { finish(profile(2, 'Second User')) })
  expect(screen.getByText('Second User')).toBeTruthy()
  act(() => {
    localStorage.removeItem('be_token')
    window.dispatchEvent(new StorageEvent('storage', { key: 'be_token' }))
  })
  expect(await screen.findByText('Signed out')).toBeTruthy()
})
