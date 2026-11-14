import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ExtensionControls from './ExtensionControls'
import ProtectedControls from './ProtectedControls'

test('extension requests send a proposed deadline and a reason', async () => {
  const act = vi.fn().mockResolvedValue(true)
  render(<ExtensionControls payment={{ actions: ['request-extension'] }} onAction={act} busy={false} />)
  fireEvent.change(screen.getByLabelText('Reason for extension'), { target: { value: 'Allow more time for final delivery.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Request extension' }))
  await waitFor(() => expect(act).toHaveBeenCalled())
  expect(act.mock.calls[0][0]).toBe('request-extension')
  expect(act.mock.calls[0][1].deadline).toMatch(/Z$/)
})

test('the other party can accept or decline an extension', () => {
  const act = vi.fn()
  render(<ExtensionControls payment={{ actions: ['decide-extension'], extension: {
    status: 'pending', deadline: '2027-01-01T00:00:00Z', reason: 'Schedule change' } }} onAction={act} busy={false} />)
  fireEvent.click(screen.getByRole('button', { name: 'Accept extension' }))
  fireEvent.click(screen.getByRole('button', { name: 'Decline extension' }))
  expect(act.mock.calls).toEqual([['decide-extension', { decision: 'accept' }], ['decide-extension', { decision: 'decline' }]])
})

test('cancellation and dispute forms submit reasons', async () => {
  const act = vi.fn().mockResolvedValue(true)
  render(<ProtectedControls payment={{ category: 'booking', actions: ['cancel', 'dispute'], rules: {}, escrow: {} }} onAction={act} busy={false} />)
  fireEvent.change(screen.getByLabelText('Cancel booking'), { target: { value: 'The reservation is no longer required.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Cancel booking' }))
  fireEvent.change(screen.getByLabelText('Open dispute'), { target: { value: 'The service was not delivered as agreed.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Open dispute' }))
  await waitFor(() => expect(act).toHaveBeenCalledWith('dispute', { reason: 'The service was not delivered as agreed.' }))
  expect(act).toHaveBeenCalledWith('cancel', { reason: 'The reservation is no longer required.' })
})
