import { get, post } from './client'
export const protectedPayments = {
  categories: () => get('/protected/categories'),
  providers: () => get('/protected/providers'),
  createDelivery: (body) => post('/protected/delivery', body),
  create: (body) => post('/protected', body),
  detail: (id) => get(`/protected/${id}`),
  act: (id, action, body = {}) => post(`/protected/${id}/${action}`, body),
  reports: () => get('/merchant/sales'),
  adminDetail: (id) => get(`/admin/protected/${id}`),
  admin: () => get('/admin/analytics'),
  disputes: () => get('/admin/disputes'),
  resolve: (id, body) => post(`/admin/disputes/${id}/resolve`, body),
}
