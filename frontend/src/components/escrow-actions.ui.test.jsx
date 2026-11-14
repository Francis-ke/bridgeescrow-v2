import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import EscrowActions from './EscrowActions'
import { escrows } from '../api/endpoints'
vi.mock('../api/endpoints', () => ({ escrows: { release: vi.fn(), confirm: vi.fn() } }))
test('opens the release code input when the server sends an SMS without returning its code', async () => {
  escrows.release.mockResolvedValue({ status: 'code_sent' })
  escrows.confirm.mockResolvedValue({})
  render(<EscrowActions escrow={{ id: 7, status: 'funded' }} reload={vi.fn()} />)
  fireEvent.click(screen.getByRole('button', { name: 'Release funds' }))
  const input = await screen.findByPlaceholderText('6-digit code')
  fireEvent.change(input, { target: { value: '123456' } })
  fireEvent.click(screen.getByRole('button', { name: 'Confirm' }))
  await waitFor(() => expect(escrows.confirm).toHaveBeenCalledWith(7, '123456'))
  expect(screen.queryByText('Release code:')).toBeNull()
})
