import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LivePayment from './LivePayment'

test('live checkout requests payment only to the verified account phone and waits for confirmation', async () => {
  const pay = vi.fn().mockResolvedValue({ message: 'Waiting for verified provider confirmation.', payment: { reference: 'PAY-1' } })
  render(<MemoryRouter><LivePayment order={{ verified_phone: '254711111111' }} onPay={pay} onRefresh={() => {}} /></MemoryRouter>)
  fireEvent.click(screen.getByRole('button', { name: 'Request M-PESA payment' }))
  await screen.findByText(/Waiting for verified provider confirmation/)
  expect(pay).toHaveBeenCalledWith({ method: 'mpesa', phone_number: '254711111111' })
  expect(screen.getByRole('button', { name: 'Request M-PESA payment' }).disabled).toBe(true)
})
