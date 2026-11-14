import { vi, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import PaymentAction from '../PaymentAction'
vi.mock('../../api/protected', () => ({ protectedPayments: { categories: vi.fn().mockResolvedValue({
  categories: [{ id: 'freelancing', label: 'Freelancing Payment' }, { id: 'booking', label: 'Booking Payment' }],
}) } }))
test('the legacy buy entry cannot show the old card form', async () => {
  render(<MemoryRouter><PaymentAction mode="buy" /></MemoryRouter>)
  await screen.findByRole('link', { name: /Freelancing Payment/ })
  expect(screen.getByRole('link', { name: /Booking Payment/ })).toBeTruthy()
  expect(screen.queryByText('Card information')).toBeNull()
  expect(screen.queryByText('Seller or business')).toBeNull()
})
