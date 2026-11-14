import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import WorkMilestone from './WorkMilestone'
import ProtectedControls from './ProtectedControls'
vi.mock('../../context/AuthContext', () => ({ useAuth: () => ({ user: { id: 1 } }) }))
const payment = { category: 'freelancing', escrow: { transaction: { sender: { id: 1 } } },
  rules: { max_revisions: 3 }, actions: ['approve'], milestones: [] }
test('approval and revision buttons invoke the correct milestone actions', async () => {
  const onAction = vi.fn().mockResolvedValue(true)
  render(<WorkMilestone item={{ id: 8, title: 'Design', amount: '100', state: 'submitted',
    deadline: '2027-01-01T00:00:00Z', submission: 'Complete design submission', revision_count: 0 }}
    payment={payment} ready busy={false} onAction={onAction} />)
  fireEvent.click(screen.getByRole('button', { name: /Approve and release/ }))
  expect(onAction).toHaveBeenCalledWith('approve', { milestone_id: 8 })
  fireEvent.change(screen.getByLabelText('Request revisions'), { target: { value: 'Please revise the final design layout.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Request revisions' }))
  await waitFor(() => expect(onAction).toHaveBeenCalledWith('revise', {
    milestone_id: 8, reason: 'Please revise the final design layout.' }))
})
test('acceptance, funding and booking confirmation buttons call live action handlers', () => {
  const onAction = vi.fn()
  render(<ProtectedControls payment={{ ...payment, category: 'booking', state: 'funded',
    escrow: { amount: '100' }, actions: ['accept', 'fund', 'confirm'] }} onAction={onAction} busy={false} />)
  fireEvent.click(screen.getByRole('button', { name: /Accept terms/ }))
  fireEvent.click(screen.getByRole('button', { name: /Secure KES/ }))
  fireEvent.click(screen.getByRole('button', { name: /Confirm service/ }))
  expect(onAction.mock.calls.map(([action]) => action)).toEqual(['accept', 'fund', 'confirm'])
})
