import { beforeEach, expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DeveloperApi from './DeveloperApi'
import { developerApi as api } from '../../api/developer'
vi.mock('../../api/developer', () => ({ developerApi: {
  apps: vi.fn(), createApp: vi.fn(), editApp: vi.fn(), keys: vi.fn(), webhooks: vi.fn(), sandbox: vi.fn(),
} }))
const app = { id: 5, app_id: 'app_public', name: 'My Store', description: 'A protected shopping store',
  website: 'https://store.example', type: 'website', environment: 'sandbox', active: true }
beforeEach(() => {
  vi.clearAllMocks(); api.apps.mockResolvedValue({ applications: [] })
  api.keys.mockResolvedValue({ credentials: [] }); api.webhooks.mockResolvedValue({ webhooks: [] })
  api.sandbox.mockResolvedValue({ available: '0.00', held: '0.00', refunded: '0.00', transactions: [] })
})
test('creates an application, selects its details and deactivates it without enabling production', async () => {
  api.createApp.mockResolvedValue({ application: app })
  api.editApp.mockResolvedValue({ application: { ...app, active: false } })
  render(<MemoryRouter><DeveloperApi /></MemoryRouter>)
  await screen.findByText('Create your first application to generate sandbox credentials.')
  fireEvent.change(screen.getByLabelText('Application name'), { target: { value: app.name } })
  fireEvent.change(screen.getByLabelText('Application description'), { target: { value: app.description } })
  fireEvent.change(screen.getByLabelText('Website URL (optional)'), { target: { value: app.website } })
  fireEvent.click(screen.getByRole('button', { name: 'Create application' }))
  await screen.findByText('Application details')
  expect(api.createApp).toHaveBeenCalledWith(expect.objectContaining({ name: app.name, environment: 'sandbox' }))
  expect(screen.getByDisplayValue('app_public').readOnly).toBe(true)
  fireEvent.click(screen.getByRole('button', { name: 'Deactivate application' }))
  await screen.findByText('Inactive applications cannot authorize external API requests.')
  expect(api.editApp).toHaveBeenCalledWith(5, { active: false })
  expect(screen.getByRole('button', { name: 'Generate credentials' }).disabled).toBe(true)
  expect(screen.getByText('Sandbox only · Production disabled')).toBeTruthy()
})
test('edits selected application settings and leaves the creation form independent', async () => {
  api.apps.mockResolvedValue({ applications: [app] })
  api.editApp.mockResolvedValue({ application: { ...app, name: 'Updated Store' } })
  render(<MemoryRouter><DeveloperApi /></MemoryRouter>)
  fireEvent.click(await screen.findByRole('button', { name: 'Edit settings' }))
  const details = screen.getByRole('button', { name: 'Save settings' }).closest('form')
  fireEvent.change(within(details).getByLabelText('Application name'), { target: { value: 'Updated Store' } })
  fireEvent.click(within(details).getByRole('button', { name: 'Save settings' }))
  await waitFor(() => expect(api.editApp).toHaveBeenCalledWith(5, expect.objectContaining({ name: 'Updated Store' })))
  await screen.findByRole('button', { name: /Updated Store/ })
  expect(screen.getByLabelText('Application name').value).toBe('')
})
