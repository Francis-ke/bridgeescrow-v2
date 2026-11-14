import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DisputeResolution from './DisputeResolution'
import { protectedPayments as api } from '../../api/protected'
vi.mock('../../api/protected', () => ({ protectedPayments: { resolve: vi.fn() } }))
test('administrator can review evidence and submit an explicit split resolution', async () => {
  api.resolve.mockResolvedValue({ dispute: { status: 'resolved' } })
  const reload = vi.fn().mockResolvedValue()
  render(<MemoryRouter><DisputeResolution dispute={{ id: 13, escrow_id: 77,
    category: 'booking', protected: true, reason: 'Booked service was not provided.' }} onDone={reload} /></MemoryRouter>)
  expect(screen.getByRole('link', { name: /Review payment/ }).getAttribute('href')).toBe('/admin/payments/77')
  fireEvent.change(screen.getByLabelText('Resolution'), { target: { value: 'split' } })
  fireEvent.change(screen.getByLabelText('Refund to client (%)'), { target: { value: '35' } })
  fireEvent.change(screen.getByLabelText('Resolution reason'), { target: { value: 'The reviewed booking terms support this split.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Resolve dispute' }))
  await waitFor(() => expect(api.resolve).toHaveBeenCalledWith(13, {
    outcome: 'split', refund_percent: 35, resolution: 'The reviewed booking terms support this split.' }))
  expect(reload).toHaveBeenCalled()
})
