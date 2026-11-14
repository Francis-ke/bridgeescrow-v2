import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import WorkMilestone from './WorkMilestone'
vi.mock('../../context/AuthContext', () => ({ useAuth: () => ({ user: { id: 2 } }) }))
test('freelancer can submit work for the selected milestone', async () => {
  const act = vi.fn().mockResolvedValue(true)
  render(<WorkMilestone item={{ id: 3, title: 'First task', amount: '100', state: 'pending', deadline: '2027-01-01T00:00:00Z' }}
    payment={{ actions: ['submit'], escrow: { transaction: { sender: { id: 1 } } } }} onAction={act} ready busy={false} />)
  fireEvent.change(screen.getByLabelText('Work details or delivery link'), { target: { value: 'All files uploaded to the agreed project location.' } })
  fireEvent.click(screen.getByRole('button', { name: 'Submit work' }))
  await waitFor(() => expect(act).toHaveBeenCalledWith('submit', {
    milestone_id: 3, submission: 'All files uploaded to the agreed project location.' }))
})
