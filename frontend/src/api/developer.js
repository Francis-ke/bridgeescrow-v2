import { get, post, request } from './client'
const patch = (path, body) => request(path, { method: 'PATCH', body })
const base = '/v1/developer'
export const developerApi = {
  apps: () => get(`${base}/apps`),
  createApp: (body) => post(`${base}/apps`, body),
  app: (id) => get(`${base}/apps/${id}`),
  editApp: (id, body) => patch(`${base}/apps/${id}`, body),
  keys: (id) => get(`${base}/apps/${id}/keys`),
  createKey: (id, body) => post(`${base}/apps/${id}/keys`, body),
  revokeKey: (id) => request(`${base}/keys/${id}`, { method: 'DELETE' }),
  rotateKey: (id) => post(`${base}/keys/${id}/rotate`, {}),
  webhooks: (id) => get(`${base}/apps/${id}/webhooks`),
  createWebhook: (id, body) => post(`${base}/apps/${id}/webhooks`, body),
  editWebhook: (id, body) => patch(`${base}/webhooks/${id}`, body),
  rotateWebhook: (id) => post(`${base}/webhooks/${id}/rotate-secret`, {}),
  testWebhook: (id) => post(`${base}/webhooks/${id}/test`, {}),
  deliveries: (id) => get(`${base}/webhooks/${id}/deliveries`),
  retryDelivery: (id) => post(`${base}/webhook-deliveries/${id}/retry`, {}),
  sandbox: (id) => get(`${base}/apps/${id}/sandbox`),
  confirmDelivery: (appId, escrowId, code) => post(`${base}/apps/${appId}/escrows/${escrowId}/delivery-confirmations`, { code }),
}
