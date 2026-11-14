const BASE = import.meta.env.VITE_API_URL || ''

export class ApiError extends Error {
  constructor(message, status, code) {
    super(message)
    this.status = status
    this.code = code
  }
}

function token() {
  return localStorage.getItem('be_token') || ''
}

export async function request(path, { method = 'GET', body, auth = true, headers: extraHeaders = {} } = {}) {
  const headers = { 'Content-Type': 'application/json', ...extraHeaders }
  const requestToken = auth ? token() : ''
  if (requestToken) headers.Authorization = `Bearer ${requestToken}`
  const res = await fetch(`${BASE}/api${path}`, {
    method,
    cache: 'no-store',
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const text = await res.text()
  let data = {}
  try { data = text ? JSON.parse(text) : {} }
  catch { throw new ApiError(res.ok ? 'The server returned an invalid response' : 'The server could not complete this request. Please try again.', res.status, 'invalid_response') }
  if (!res.ok) {
    const err = data.error || {}
    if (res.status === 401 && ['token_expired', 'token_invalid'].includes(err.code) &&
        requestToken && requestToken === token()) {
      window.dispatchEvent(new Event('session-expired'))
    }
    throw new ApiError(err.message || 'Request failed', res.status, err.code)
  }
  if (auth && method !== 'GET') window.dispatchEvent(new Event('account-updated'))
  return data
}

export const get = (p) => request(p)
export const post = (p, body) => request(p, { method: 'POST', body })
export const put = (p, body) => request(p, { method: 'PUT', body })
