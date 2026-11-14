import { expect, test } from 'vitest'
import { fireEvent, render, screen, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import WalletBalances from './WalletBalances'

const balances = { available: '20.00', escrow: '10.00', incoming_escrow: '5.00',
  website_sandbox: { application_count: 1, available: '0.00', escrow: '100.00' } }
function card(title) { return within(screen.getByRole('heading', { name: title }).closest('section')) }
test('website funds move from escrow to available and account wallet stays separate', () => {
  const { rerender } = render(<MemoryRouter><WalletBalances balances={balances} /></MemoryRouter>)
  expect(card('Available Balance').getByText('20.00')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Website sandbox' }))
  expect(card('Escrow Balance').getByText('100.00')).toBeTruthy()
  expect(card('Available Balance').getByText('0.00')).toBeTruthy()
  const released = { ...balances, website_sandbox: { application_count: 1, available: '99.00', escrow: '0.00' } }
  rerender(<MemoryRouter><WalletBalances balances={released} /></MemoryRouter>)
  expect(card('Available Balance').getByText('99.00')).toBeTruthy()
  expect(card('Escrow Balance').getByText('0.00')).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'My wallet' }))
  expect(card('Available Balance').getByText('20.00')).toBeTruthy()
  expect(card('Escrow Balance').getByText('15.00')).toBeTruthy()
})
test('accounts without API applications see their normal wallet', () => {
  render(<MemoryRouter><WalletBalances balances={{ ...balances, website_sandbox: { application_count: 0 } }} /></MemoryRouter>)
  expect(screen.queryByRole('button', { name: 'Website sandbox' })).toBeNull()
  expect(card('Available Balance').getByText('20.00')).toBeTruthy()
})
