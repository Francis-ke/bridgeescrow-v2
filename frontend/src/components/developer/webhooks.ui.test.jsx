import { beforeEach, expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import Webhooks from './Webhooks'
import { developerApi as api } from '../../api/developer'
vi.mock('../../api/developer', () => ({ developerApi: {
  webhooks: vi.fn(), createWebhook: vi.fn(), testWebhook: vi.fn(), deliveries: vi.fn(), retryDelivery: vi.fn(),
} }))
const endpoint = { id: 9, url: 'https://store.example/events', active: true, events: ['escrow.held'] }
beforeEach(() => { vi.clearAllMocks(); api.webhooks.mockResolvedValue({ webhooks: [] }) })
test('registers a signed webhook, reveals its secret once and queues a test delivery', async () => {
  api.createWebhook.mockImplementation(async () => {
    api.webhooks.mockResolvedValue({ webhooks: [endpoint] })
    return { webhook: endpoint, signing_secret: 'be_whsec_once' }
  })
  api.testWebhook.mockResolvedValue({ queued: true })
  api.deliveries.mockResolvedValue({ deliveries: [{ id: 4, event_id: 'evt_1', event_type: 'payment.pending', status: 'failed', attempts: 1, response_status: 503, last_error: 'Temporarily unavailable' }] })
  api.retryDelivery.mockResolvedValue({ delivery: { id: 4, status: 'retry' } })
  render(<Webhooks application={{ id: 5, active: true }} />)
  fireEvent.change(screen.getByLabelText('HTTPS webhook URL'), { target: { value: endpoint.url } })
  fireEvent.click(screen.getByRole('button', { name: 'Register webhook' }))
  await screen.findByDisplayValue('be_whsec_once')
  expect(api.createWebhook).toHaveBeenCalledWith(5, expect.objectContaining({ url: endpoint.url, events: expect.arrayContaining(['escrow.held']) }))
  fireEvent.click(screen.getByRole('button', { name: 'Dismiss signing secret' }))
  expect(screen.queryByDisplayValue('be_whsec_once')).toBeNull()
  fireEvent.click(screen.getByRole('button', { name: 'Send test event' }))
  await screen.findByText('Temporarily unavailable')
  expect(api.testWebhook).toHaveBeenCalledWith(9)
  expect(screen.getByText('Attempts: 1 · HTTP 503')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Retry delivery' }))
  await waitFor(() => expect(api.retryDelivery).toHaveBeenCalledWith(4))
})
