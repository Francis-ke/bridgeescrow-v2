import { vi, test, expect } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ApiKeyForm from './ApiKeyForm'
import ApiKeys from './ApiKeys'
import SellerOrders from './SellerOrders'

test('seller details create an API key and existing keys can be revoked', () => {
  const create = vi.fn(), revoke = vi.fn()
  render(<><ApiKeyForm initial={{ business_name: 'Shop', website: 'https://shop.example', contact_email: 'shop@example.com', key_name: 'Website' }} onCreate={create} />
    <ApiKeys keys={[{ id: 1, name: 'Website', prefix: 'be_sk_', revoked: false }]} secret="one-time-secret" onRevoke={revoke} /></>)
  fireEvent.click(screen.getByRole('button', { name: 'Create API key' }))
  expect(create).toHaveBeenCalledWith(expect.objectContaining({ business_name: 'Shop' }))
  fireEvent.click(screen.getByRole('button', { name: 'Revoke' }))
  expect(revoke).toHaveBeenCalledWith(1)
  expect(screen.getByText('one-time-secret')).toBeTruthy()
})

test('delivery redemption submits the buyer code for the specific seller order', () => {
  const redeem = vi.fn()
  render(<SellerOrders orders={[{ id: 7, order_id: 'SHOP-7', amount: '300.00', state: 'paid',
    checkout_url: '/checkout/token' }]} redeem={redeem} busy={false} />)
  fireEvent.change(screen.getByLabelText('Delivery code for SHOP-7'), { target: { value: '01234567' } })
  fireEvent.click(screen.getByRole('button', { name: 'Confirm delivery & release' }))
  expect(redeem).toHaveBeenCalledWith(7, '01234567')
})
