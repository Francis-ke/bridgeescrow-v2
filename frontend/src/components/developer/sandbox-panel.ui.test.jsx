import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import SandboxPanel from './SandboxPanel'
import { developerApi as api } from '../../api/developer'
vi.mock('../../api/developer', () => ({ developerApi: { sandbox: vi.fn(), confirmDelivery: vi.fn() } }))
test('redeems a buyer delivery code for an owned held order and refreshes its sandbox balance', async () => {
  const order = { id: 12, order_id: 'SHOP-12', state: 'HELD', amount: '300.00' }
  api.sandbox.mockResolvedValueOnce({ available: '0.00', held: '300.00', transactions: [order] })
  api.sandbox.mockResolvedValue({ available: '297.00', held: '0.00', transactions: [{ ...order, state: 'RELEASED' }] })
  api.confirmDelivery.mockResolvedValue({ escrow: { state: 'RELEASED' } })
  render(<SandboxPanel application={{ id: 5, active: true }} />)
  fireEvent.change(await screen.findByLabelText('Delivery code for SHOP-12'), { target: { value: '12345678' } })
  fireEvent.click(screen.getByRole('button', { name: 'Confirm delivery' }))
  await screen.findByText('RELEASED')
  expect(api.confirmDelivery).toHaveBeenCalledWith(5, 12, '12345678')
  await waitFor(() => expect(api.sandbox).toHaveBeenCalledTimes(2))
  expect(screen.getByText('KES 297.00')).toBeTruthy()
  expect(screen.queryByLabelText('Delivery code for SHOP-12')).toBeNull()
})
