import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import PaymentSelection from './PaymentSelection'
import ProtectedNew from './ProtectedNew'
import { protectedPayments as api } from '../../api/protected'
vi.mock('../../api/protected', () => ({ protectedPayments: {
  categories: vi.fn(), providers: vi.fn(), create: vi.fn(),
} }))
const categories = ['delivery', 'services', 'events', 'deposits', 'contracts', 'other', 'freelancing', 'booking']
const defaults = { release: 'mutual_confirmation', late_refund_percent: 0,
  early_refund_percent: 100, max_extension_hours: 168, max_revisions: 3, revision_hours: 48 }
function setup(category) {
  api.categories.mockResolvedValue({ categories: categories.map((id) => ({ id, label: id, defaults })) })
  api.providers.mockResolvedValue({ providers: [{ id: 2, name: 'Provider', email: 'provider@example.com' }] })
  api.create.mockResolvedValue({ payment: { escrow: { id: 77 } } })
  render(<MemoryRouter initialEntries={[`/protected/new/${category}`]}><Routes>
    <Route path="/protected/new/:category" element={<ProtectedNew />} />
    <Route path="/escrows/:id" element={<p>Payment created</p>} />
  </Routes></MemoryRouter>)
}
test('all eight categories link to functional creation routes', async () => {
  api.categories.mockResolvedValue({ categories: categories.map((id) => ({ id, label: id })) })
  render(<MemoryRouter><PaymentSelection /></MemoryRouter>)
  await screen.findByRole('link', { name: /freelancing/i })
  expect(screen.getAllByRole('link')).toHaveLength(8)
  expect(screen.getByRole('link', { name: /booking/i }).getAttribute('href')).toBe('/protected/new/booking')
})
test('booking form submits explicit cancellation policy and ISO booking dates', async () => {
  setup('booking')
  await screen.findByLabelText('Provider')
  fireEvent.change(screen.getByLabelText('Provider'), { target: { value: '2' } })
  fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'Hotel reservation' } })
  fireEvent.change(screen.getByLabelText('Service description and agreed terms'), { target: { value: 'Reserve accommodation with the selected provider.' } })
  fireEvent.change(screen.getByLabelText('Total amount (KES)'), { target: { value: '100' } })
  fireEvent.change(screen.getByLabelText('Refund after deadline (%)'), { target: { value: '35' } })
  fireEvent.click(screen.getByRole('button', { name: 'Create protected payment' }))
  await screen.findByText('Payment created')
  const payload = api.create.mock.calls.at(-1)[0]
  expect(payload.category).toBe('booking')
  expect(payload.rules.late_refund_percent).toBe(35)
  expect(payload.booking_start).toMatch(/Z$/)
})
test('freelancing form supports optional milestone inputs and provider acceptance', async () => {
  setup('freelancing')
  await screen.findByLabelText('Freelancer')
  fireEvent.click(screen.getByRole('button', { name: 'Add milestone' }))
  expect(screen.getByLabelText('Milestone 1 title')).toBeTruthy()
  expect(screen.getByLabelText('Milestone deadline')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Remove milestone' }))
  await waitFor(() => expect(screen.queryByLabelText('Milestone 1 title')).toBeNull())
})
