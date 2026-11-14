import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import HostedCheckout from './HostedCheckout'
import { checkoutApi } from '../../api/integrations'
vi.mock('../../api/integrations', () => ({ checkoutApi: vi.fn() }))
vi.mock('../../components/integration/BuyerVerification', () => ({ default: ({ onVerified }) => <button onClick={() => onVerified('scoped')}>Verify email</button> }))
const order = { id: 1, order_id: 'SANDBOX-1', state: 'pending', amount: '300.00', environment: 'sandbox',
  seller: { name: 'Sandbox Shop' }, items: [{ description: 'Package', quantity: 1, line_cents: 30000 }] }
function mount() {
  render(<MemoryRouter initialEntries={['/checkout/order-token?method=mpesa']}><Routes>
    <Route path="/checkout/:token" element={<HostedCheckout />} />
  </Routes></MemoryRouter>)
}
test('sandbox M-PESA uses the session method, records failure, and releases only on buyer confirmation', async () => {
  let state = 'pending'
  checkoutApi.mockImplementation(async (token, action) => {
    if (action === 'pay') state = 'paid'
    if (action === 'confirm') state = 'completed'
    return { order: { ...order, state, code_email_sent: true } }
  })
  mount(); fireEvent.click(await screen.findByRole('button', { name: 'Verify email' }))
  await screen.findByLabelText('M-PESA phone number')
  fireEvent.click(screen.getByRole('button', { name: 'Simulate payment failure' }))
  await screen.findByText(/Test failure recorded/)
  expect(checkoutApi).toHaveBeenCalledWith('order-token', 'sandbox-failure', { method: 'mpesa' }, 'scoped')
  fireEvent.change(screen.getByLabelText('M-PESA phone number'), { target: { value: '254712345678' } })
  fireEvent.click(screen.getByRole('button', { name: 'Confirm sandbox M-PESA payment' }))
  await screen.findByText('Payment protected')
  expect(checkoutApi).toHaveBeenCalledWith('order-token', 'pay', { method: 'mpesa', phone_number: '254712345678' }, 'scoped')
  fireEvent.click(screen.getByRole('button', { name: 'Confirm completion and release sandbox funds' }))
  await screen.findByText('Delivery confirmed')
  expect(checkoutApi).toHaveBeenCalledWith('order-token', 'confirm', {}, 'scoped')
})
test('a verified sandbox buyer can open a dispute without a normal wallet session', async () => {
  let state = 'paid'
  checkoutApi.mockImplementation(async (token, action) => {
    if (action === 'dispute') state = 'disputed'
    return { order: { ...order, state, code_email_sent: true } }
  })
  mount(); fireEvent.click(await screen.findByRole('button', { name: 'Verify email' }))
  fireEvent.change(await screen.findByLabelText('Dispute reason'), { target: { value: 'Package did not arrive at the agreed address.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Open a dispute' }))
  await screen.findByText('Payment disputed')
  expect(checkoutApi).toHaveBeenCalledWith('order-token', 'dispute', { reason: 'Package did not arrive at the agreed address.' }, 'scoped')
  expect(screen.queryByRole('button', { name: 'Confirm completion and release sandbox funds' })).toBeNull()
})
