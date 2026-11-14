import { beforeEach, expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Credentials from './Credentials'
import { developerApi as api } from '../../api/developer'
vi.mock('../../api/developer', () => ({ developerApi: {
  keys: vi.fn(), createKey: vi.fn(), revokeKey: vi.fn(), rotateKey: vi.fn(),
} }))
const application = { id: 7, active: true }
const key = { id: 11, name: 'Server integration', public_key: 'be_test_pk_public',
  prefix: 'be_test_sk_prefix', active: true, permissions: ['escrow:read'] }
beforeEach(() => { vi.clearAllMocks(); api.keys.mockResolvedValue({ credentials: [] }) })
test('generates scoped credentials, copies a secret once, and revokes the selected key', async () => {
  const copy = vi.fn().mockResolvedValue()
  Object.defineProperty(navigator, 'clipboard', { configurable: true, value: { writeText: copy } })
  api.createKey.mockImplementation(async () => {
    api.keys.mockResolvedValue({ credentials: [key] })
    return { credential: key, secret_key: 'be_test_sk_once' }
  })
  api.revokeKey.mockImplementation(async () => {
    api.keys.mockResolvedValue({ credentials: [{ ...key, active: false }] })
    return { credential: { ...key, active: false } }
  })
  render(<Credentials application={application} />)
  fireEvent.click(screen.getByRole('button', { name: 'Generate credentials' }))
  await screen.findByDisplayValue('be_test_sk_once')
  expect(api.createKey).toHaveBeenCalledWith(7, expect.objectContaining({ permissions: expect.arrayContaining(['escrow:read', 'checkout:write']) }))
  fireEvent.click(screen.getByRole('button', { name: 'Copy Sandbox secret key' }))
  await waitFor(() => expect(copy).toHaveBeenCalledWith('be_test_sk_once'))
  fireEvent.click(screen.getByRole('button', { name: 'Revoke key' }))
  await screen.findByText('Revoked')
  expect(api.revokeKey).toHaveBeenCalledWith(11)
  expect(screen.queryByDisplayValue('be_test_sk_once')).toBeNull()
})
test('does not reveal stored secrets on reload and reports ownership failures', async () => {
  api.keys.mockResolvedValueOnce({ credentials: [key] })
  const view = render(<Credentials application={application} />)
  await screen.findByDisplayValue(key.public_key)
  expect(screen.queryByText('Save these credentials now')).toBeNull()
  view.unmount(); api.keys.mockRejectedValueOnce(new Error('Application not found.'))
  render(<Credentials application={{ id: 999, active: true }} />)
  await screen.findByText('Application not found.')
  expect(screen.queryByDisplayValue(key.public_key)).toBeNull()
})
