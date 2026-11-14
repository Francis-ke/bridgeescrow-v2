import { expect, test, vi } from 'vitest'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from './Dashboard'
import { wallet } from '../api/endpoints'
let user
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user }) }))
vi.mock('../api/endpoints', () => ({ wallet: { get: vi.fn(), ledger: vi.fn() } }))
vi.mock('../components/VirtualCard', () => ({ default: () => null }))
vi.mock('../components/QuickActions', () => ({ default: () => null }))
const own = (id, available, escrow) => ({ wallet: {
  user_id: id, available, escrow, incoming_escrow: '0.00',
} })
const view = () => <MemoryRouter><Dashboard /></MemoryRouter>

test('switching accounts clears old balances and statements and ignores late responses', async () => {
  user = { id: 1, full_name: 'First User', account_number: 'BE1111111' }
  wallet.get.mockResolvedValue(own(1, '6555.00', '990.00'))
  wallet.ledger.mockResolvedValue({ entries: [{ id: 1, description: 'First private transaction', amount_cents: 100 }] })
  const { rerender } = render(view())
  await screen.findByText('6,555.00')
  fireEvent.click(screen.getByRole('button', { name: 'View Statements' }))
  await screen.findByText('First private transaction')
  let finish
  wallet.get.mockImplementationOnce(() => new Promise((resolve) => { finish = resolve }))
  act(() => { window.dispatchEvent(new Event('focus')) })
  user = { id: 2, full_name: 'Second User', account_number: 'BE2222222' }
  wallet.get.mockResolvedValue(own(2, '25.00', '0.00'))
  rerender(view())
  expect(screen.queryByText('6,555.00')).toBeNull()
  expect(screen.queryByText('First private transaction')).toBeNull()
  await screen.findByText('25.00')
  await act(async () => { finish(own(1, '6555.00', '990.00')) })
  expect(screen.queryByText('6,555.00')).toBeNull()
  expect(screen.getByText('25.00')).toBeTruthy()
})

test('a wallet response belonging to another user is never displayed', async () => {
  user = { id: 3, full_name: 'Third User', account_number: 'BE3333333' }
  wallet.get.mockResolvedValue(own(1, '6555.00', '990.00'))
  render(view())
  await waitFor(() => expect(wallet.get).toHaveBeenCalled())
  expect(screen.queryByText('6,555.00')).toBeNull()
})
