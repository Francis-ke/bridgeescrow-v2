import { expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, useLocation } from 'react-router-dom'
import App from '../../App'
vi.mock('../../context/AuthContext', () => ({ useAuth: () => ({ user: { id: 1, role: 'user' }, loading: false, signOut: vi.fn() }) }))
vi.mock('../../components/NotificationBell', () => ({ default: () => null }))
vi.mock('./DeveloperApi', () => ({ default: () => <h1>Developer workspace</h1> }))
function Location() { return <p>{useLocation().pathname}</p> }
test('old seller URL redirects to Developer API and the menu uses the new name', async () => {
  render(<MemoryRouter initialEntries={['/seller/api']}><App /><Location /></MemoryRouter>)
  await screen.findByRole('heading', { name: 'Developer workspace' })
  expect(screen.getByText('/developers/api')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Open navigation' }))
  expect(screen.getByRole('link', { name: 'Developer API' }).getAttribute('href')).toBe('/developers/api')
  expect(screen.getByRole('link', { name: 'Home' })).toBeTruthy()
  expect(screen.getByRole('link', { name: 'My escrows' })).toBeTruthy()
  expect(screen.getByRole('button', { name: 'Sign out' })).toBeTruthy()
  expect(screen.queryByRole('link', { name: 'Seller API' })).toBeNull()
})
