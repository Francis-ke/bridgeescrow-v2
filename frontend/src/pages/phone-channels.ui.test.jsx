import { beforeEach, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import PhoneChannels from './PhoneChannels'
import { phoneApi } from '../api/phone'
import { auth } from '../api/endpoints'
let profile
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: profile, updateUser: (value) => { profile = value } }) }))
vi.mock('../api/endpoints', () => ({ auth: { setPin: vi.fn() } }))
vi.mock('../api/phone', () => ({ phoneApi: { status: vi.fn(), start: vi.fn(), verify: vi.fn(), messages: vi.fn(), testSms: vi.fn(), dial: vi.fn() } }))
beforeEach(() => {
  vi.clearAllMocks(); profile = { id: 1, phone_verified: false }
  phoneApi.status.mockResolvedValue({ sms_mode: 'simulated', payment_mode: 'simulated', ussd_service_code: '' })
  phoneApi.messages.mockResolvedValue({ sms_mode: 'simulated', messages: [] })
  phoneApi.start.mockResolvedValue({ challenge_id: 'challenge-1' })
  phoneApi.verify.mockResolvedValue({ user: { id: 1, phone: '254711111111', phone_verified: true } })
  auth.setPin.mockResolvedValue({ status: 'pin_set' })
})
test('links a phone and uses the same account in the PIN-protected USSD simulator', async () => {
  render(<MemoryRouter><PhoneChannels /></MemoryRouter>)
  expect(screen.getByRole('button', { name: 'Start session' }).disabled).toBe(true)
  fireEvent.change(screen.getByLabelText('Phone number'), { target: { value: '0711111111' } })
  fireEvent.click(screen.getByRole('button', { name: 'Send verification code' }))
  await screen.findByLabelText('SMS verification code')
  fireEvent.change(screen.getByLabelText('SMS verification code'), { target: { value: '123456' } })
  fireEvent.click(screen.getByRole('button', { name: 'Verify phone' }))
  await screen.findByText(/Verified: \+254711111111/)
  expect(phoneApi.verify).toHaveBeenCalledWith('challenge-1', '123456')
  phoneApi.dial.mockResolvedValueOnce({ reply: 'CON Enter your BridgeEscrow transaction PIN' })
  fireEvent.click(screen.getByRole('button', { name: 'Start session' }))
  await screen.findByText('Enter your BridgeEscrow transaction PIN')
  fireEvent.change(screen.getByLabelText('USSD response'), { target: { value: '1234' } })
  phoneApi.dial.mockResolvedValueOnce({ reply: 'CON Karibu BridgeEscrow\n1. Check balance' })
  fireEvent.click(screen.getByRole('button', { name: 'Send response' }))
  await screen.findByText(/1. Check balance/)
  expect(phoneApi.dial).toHaveBeenLastCalledWith(expect.any(String), '1234')
  expect(screen.getByText('Simulated SMS inbox')).toBeTruthy()
})
