import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import ProtectedNew from './ProtectedNew'
import { protectedPayments as api } from '../../api/protected'
vi.mock('../../api/protected', () => ({ protectedPayments: {
  createDelivery: vi.fn().mockResolvedValue({ payment: { escrow: { id: 71 } } }),
} }))
test('delivery carries amount and duration into the receiving-card form without a password', async () => {
  render(<MemoryRouter initialEntries={['/protected/new/delivery']}><Routes>
    <Route path="/protected/new/:category" element={<ProtectedNew />} />
    <Route path="/escrows/:id" element={<p>Created delivery</p>} />
  </Routes></MemoryRouter>)
  expect(screen.queryByLabelText('Title')).toBeNull()
  fireEvent.change(screen.getByLabelText('Time duration'), { target: { value: '2' } })
  fireEvent.change(screen.getByLabelText('Time unit'), { target: { value: 'days' } })
  fireEvent.change(screen.getByLabelText('Amount (KES)'), { target: { value: '100' } })
  fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
  expect(screen.queryByLabelText('Receiving account')).toBeNull()
  expect(screen.queryByLabelText('Your account password')).toBeNull()
  expect(screen.queryByLabelText('CVC security code')).toBeNull()
  expect(screen.getByLabelText('Amount (KES)').value).toBe('100')
  expect(screen.getByLabelText('Amount (KES)').readOnly).toBe(true)
  fireEvent.change(screen.getByLabelText('Other account card number'), { target: { value: '9900123456789012' } })
  fireEvent.change(screen.getByLabelText('Account holder name'), { target: { value: 'Provider' } })
  fireEvent.click(screen.getByRole('button', { name: 'Confirm transaction' }))
  await screen.findByText('Created delivery')
  expect(api.createDelivery).toHaveBeenCalledWith({ recipient_card: '9900123456789012', account_holder: 'Provider', duration_hours: 48, amount: '100' })
})
