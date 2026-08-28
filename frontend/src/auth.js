import { reactive } from 'vue'

import { activeRoute } from './activeRoute'
import { api, ensureCsrf, refreshAccess, setAccessToken } from './api'

export const auth = reactive({
  user: null,
  ready: false,
  get loggedIn() {
    return Boolean(this.user)
  },
  saveSession(data) {
    setAccessToken(data.access)
    this.user = data.user || null
  },
  async login(credentials) {
    const tokens = await api('/auth/login/', { method: 'POST', body: JSON.stringify(credentials) })
    this.saveSession(tokens)
    this.user = await api('/auth/me/')
  },
  async register(form) {
    const data = await api('/auth/register/', { method: 'POST', body: JSON.stringify(form) })
    this.saveSession(data)
  },
  async restore() {
    try {
      await ensureCsrf()
      if (await refreshAccess()) this.user = await api('/auth/me/')
    } catch {
      this.logout()
    } finally {
      this.ready = true
    }
  },
  logout() {
    void api('/auth/logout/', { method: 'POST' }).catch(() => {})
    setAccessToken()
    activeRoute.clear()
    this.user = null
  },
})
