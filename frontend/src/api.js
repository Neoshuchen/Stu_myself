const API_BASE = import.meta.env.VITE_API_BASE || '/api'
let accessToken = ''
let refreshPromise = null

/** 在当前页面内存中替换访问令牌；空值会清除会话。 */
export function setAccessToken(token = '') {
  accessToken = token
}

function csrfToken() {
  return document.cookie.split('; ').find((item) => item.startsWith('csrftoken='))?.split('=')[1] || ''
}

/** 请求同源 CSRF Cookie；成功时无返回值，失败时抛出用户可读错误。 */
export async function ensureCsrf() {
  const response = await fetch(`${API_BASE}/auth/csrf/`, { credentials: 'include' })
  if (!response.ok) throw new Error('无法建立安全会话，请稍后重试。')
}

function firstError(payload) {
  if (!payload) return '请求失败，请稍后重试。'
  if (typeof payload === 'string') return payload
  if (Array.isArray(payload)) return payload.map(firstError).join(' ')
  if (typeof payload.detail === 'string') return payload.detail
  const value = Object.values(payload)[0]
  return value ? firstError(value) : '请求失败，请稍后重试。'
}

async function requestRefresh() {
  const response = await fetch(`${API_BASE}/auth/refresh/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'X-CSRFToken': decodeURIComponent(csrfToken()) },
  })
  if (!response.ok) return false
  const data = await response.json()
  setAccessToken(data.access)
  return true
}

/** 轮换 HttpOnly 刷新 Cookie，并返回是否取得新访问令牌。 */
export async function refreshAccess() {
  // 多个请求同时遇到 401 时只轮换一次刷新令牌，否则其余请求会使用已拉黑的旧 Cookie。
  if (!refreshPromise) refreshPromise = requestRefresh().finally(() => { refreshPromise = null })
  return refreshPromise
}

/** 调用后端 API，自动附加访问令牌、CSRF 和一次 401 刷新重试。 */
export async function api(path, options = {}, retried = false) {
  const headers = new Headers(options.headers || {})
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json')
  if (options.method && !['GET', 'HEAD', 'OPTIONS'].includes(options.method.toUpperCase())) {
    headers.set('X-CSRFToken', decodeURIComponent(csrfToken()))
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers, credentials: 'include' })
  if (response.status === 401 && accessToken && !retried && await refreshAccess()) return api(path, options, true)
  if (response.status === 204) return null
  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const error = new Error(firstError(payload))
    error.payload = payload
    throw error
  }
  return payload
}
