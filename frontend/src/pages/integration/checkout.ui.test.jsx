import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import HostedCheckout from './HostedCheckout'
import { checkoutApi } from '../../api/integrations'
vi.mock('../../api/integrations', () => ({ checkoutApi: vi.fn() }))
const order = { id: 1, order_id: 'SHOP-1', state: 'pending', amount: '300.00',
  seller: { name: 'Seller Shop' }, items: [{ description: 'Package', quantity: 1, line_cents: 30000 }] }
test('buyer verifies OTP and confirms an immutable bill without transmitting card secrets', async () => {
  checkoutApi.mockImplementation(async (token, action, body, session) => {
    if (action === 'request-otp') return { challenge_id: 'challenge', email: body.email }
    if (action === 'verify') return { session_token: 'scoped-session' }
    if (action === 'pay') return { state: 'paid', code_email_sent: true }
    const paid = checkoutApi.mock.calls.some(([, method]) => method === 'pay')
    return { order: { ...order, state: paid ? 'paid' : 'pending', code_email_sent: paid } }
  })
  render(<MemoryRouter initialEntries={['/checkout/order-token']}><Routes>
    <Route path="/checkout/:token" element={<HostedCheckout />} />
  </Routes></MemoryRouter>)
  await screen.findByText('Seller Shop')
  fireEvent.change(screen.getByLabelText('Full name'), { target: { value: 'Buyer Name' } })
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'buyer@example.com' } })
  fireEvent.change(screen.getByLabelText('Phone number'), { target: { value: '0712345678' } })
  fireEvent.change(screen.getByLabelText('Delivery address'), { target: { value: 'Nairobi address' } })
  fireEvent.click(screen.getByRole('button', { name: 'Send verification OTP' }))
  await screen.findByLabelText('Email OTP')
  fireEvent.change(screen.getByLabelText('Email OTP'), { target: { value: '123456' } })
  fireEvent.click(screen.getByRole('button', { name: 'Verify and continue' }))
  await screen.findByLabelText('Card number')
  expect(screen.getByLabelText('Amount (KES)').readOnly).toBe(true)
  expect(screen.getByLabelText('Amount (KES)').value).toBe('300.00')
  fireEvent.change(screen.getByLabelText('Card number'), { target: { value: '9900123456781234' } })
  fireEvent.change(screen.getByLabelText('Expiry date'), { target: { value: '1229' } })
  fireEvent.change(screen.getByLabelText('CVC security code'), { target: { value: '123' } })
  fireEvent.change(screen.getByLabelText('Cardholder name'), { target: { value: 'Buyer Name' } })
  fireEvent.click(screen.getByRole('button', { name: 'Confirm transaction' }))
  await screen.findByText('Payment protected')
  expect(checkoutApi).toHaveBeenCalledWith('order-token', 'pay', { last4: '1234' }, 'scoped-session')
})
