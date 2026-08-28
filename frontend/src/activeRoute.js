const KEY = 'active_enrollment'

// 当前选中的学习路线。存 localStorage，这样在「今日」选好路线后切到其它页面再回来不会被重置。
export const activeRoute = {
  get() {
    return localStorage.getItem(KEY) || ''
  },
  set(id) {
    if (id) localStorage.setItem(KEY, String(id))
    else localStorage.removeItem(KEY)
  },
  clear() {
    localStorage.removeItem(KEY)
  },
}
