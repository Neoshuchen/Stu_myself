<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { activeRoute } from '../activeRoute'
import { api } from '../api'
import { auth } from '../auth'

const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)
const sidePlan = ref(null)
const notificationCount = ref(0)
let sidePlanLoadVersion = 0

const icon = (paths) => `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">${paths}</svg>`
const stroke = 'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'

const nav = [
  { to: '/dashboard', label: '今日', icon: icon(`<rect x="3" y="5" width="18" height="16" rx="3" ${stroke}/><path d="M3 10h18M8 3v4M16 3v4" ${stroke}/>`) },
  { to: '/journey', label: '学习路径', icon: icon(`<circle cx="6" cy="6" r="2.6" ${stroke}/><circle cx="18" cy="18" r="2.6" ${stroke}/><path d="M8.6 6H15a3 3 0 0 1 0 6H9a3 3 0 0 0 0 6h6.4" ${stroke}/>`) },
  { to: '/review', label: '复习中心', icon: icon(`<path d="M5 8a8 8 0 1 1-1 7" ${stroke}/><path d="M5 4v4h4M9 12l2 2 4-4" ${stroke}/>` ) },
  { to: '/insights', label: '能力图谱', icon: icon(`<circle cx="12" cy="12" r="8.5" ${stroke}/><circle cx="12" cy="12" r="4.5" ${stroke}/><circle cx="12" cy="12" r="1.2" fill="currentColor"/>`) },
  { to: '/plans', label: '发现计划', icon: icon(`<circle cx="12" cy="12" r="9" ${stroke}/><path d="M15.5 8.5l-2.2 4.8-4.8 2.2 2.2-4.8z" ${stroke}/>`) },
  { to: '/community', label: '学习社区', icon: icon(`<path d="M4 6.5A3.5 3.5 0 0 1 7.5 3h9A3.5 3.5 0 0 1 20 6.5v6a3.5 3.5 0 0 1-3.5 3.5H9.5L4 20z" ${stroke}/>`) },
  { to: '/mutual-help', label: '学习互助', icon: icon(`<path d="M12 20s-7.2-4.6-9-9.2A5.2 5.2 0 0 1 12 6.4a5.2 5.2 0 0 1 9 4.4C19.2 15.4 12 20 12 20z" ${stroke}/>`) },
  { to: '/team', label: '学习小队', icon: icon(`<circle cx="8" cy="9" r="3" ${stroke}/><circle cx="17" cy="10" r="2.5" ${stroke}/><path d="M2.8 19c.6-3.2 2.3-4.8 5.2-4.8s4.6 1.6 5.2 4.8M13.5 15.2c2.8-.7 5.1.6 5.7 3.8" ${stroke}/>` ) },
  { to: '/notifications', label: '通知', badge: true, icon: icon(`<path d="M5 17h14l-1.5-2.2V10a5.5 5.5 0 0 0-11 0v4.8zM10 20h4" ${stroke}/>` ) },
  { to: '/plans/new', label: '创建路线', exact: true, icon: icon(`<circle cx="12" cy="12" r="9" ${stroke}/><path d="M12 8v8M8 12h8" ${stroke}/>`) },
]
const adminIcon = icon(`<path d="M4 12.5l5 5L20 6.5" ${stroke}/>`)
const visibleNav = computed(() => auth.user?.is_staff ? [...nav, { to: '/admin/reviews', label: '管理中心', icon: adminIcon }] : nav)
const initials = computed(() => (auth.user?.name || '学').slice(0, 1).toUpperCase())

const learningContext = computed(() => route.path === '/dashboard' || route.path === '/journey' || route.path.startsWith('/learn/'))
// 侧栏进度卡跟随「今日」页选中的路线：URL 里没带 enrollment 时读记住的那条。
const selectedEnrollmentId = computed(() => route.params.enrollmentId || route.query.enrollment || (learningContext.value ? activeRoute.get() : ''))

function navActive(item) {
  if (item.to === '/plans/new') return route.path === item.to || route.path.endsWith('/edit')
  if (item.to === '/plans') return route.path.startsWith('/plans') && !route.path.includes('/community') && route.path !== '/plans/new' && !route.path.endsWith('/edit')
  if (item.to === '/community') return route.path.startsWith('/community') || route.path.includes('/community')
  return route.path.startsWith(item.to)
}

function logout() {
  auth.logout()
  router.push('/login')
}

async function loadSidePlan() {
  const version = ++sidePlanLoadVersion
  sidePlan.value = null
  if (!auth.loggedIn || !learningContext.value) return
  try {
    const query = selectedEnrollmentId.value ? `?enrollment=${selectedEnrollmentId.value}` : ''
    let data
    try {
      data = await api(`/dashboard/${query}`)
    } catch (err) {
      // 记住的路线可能已经退出，回落到默认路线。
      if (!query) throw err
      activeRoute.clear()
      data = await api('/dashboard/')
    }
    const e = data?.enrollment
    if (e && version === sidePlanLoadVersion) sidePlan.value = {
      title: e.plan.title,
      day: e.current_day,
      total: e.plan.total_days,
      percent: e.progress_percent,
      label: { active: '正在学习', paused: '已暂停', completed: '已完成' }[e.status],
    }
  } catch { /* 侧栏进度卡加载失败时静默降级为标语卡 */ }
}

async function loadNotificationCount() {
  if (!auth.loggedIn) return
  try {
    notificationCount.value = (await api('/notifications/unread-count/')).count
  } catch { notificationCount.value = 0 }
}

watch([learningContext, selectedEnrollmentId], loadSidePlan, { immediate: true })
watch(() => route.fullPath, loadNotificationCount, { immediate: true })
onMounted(() => window.addEventListener('notifications-changed', loadNotificationCount))
onBeforeUnmount(() => window.removeEventListener('notifications-changed', loadNotificationCount))
</script>

<template>
  <div class="app-frame">
    <header class="mobile-bar">
      <RouterLink class="brand" to="/dashboard"><span class="brand-mark">知</span><b>知序</b></RouterLink>
      <button class="icon-button" aria-label="打开导航" @click="menuOpen = !menuOpen">{{ menuOpen ? '×' : '☰' }}</button>
    </header>

    <aside class="sidebar" :class="{ open: menuOpen }">
      <RouterLink class="brand desktop-brand" to="/dashboard">
        <span class="brand-mark">知</span>
        <span><b>知序</b><small>Make today count.</small></span>
      </RouterLink>
      <nav class="main-nav" aria-label="主导航">
        <RouterLink v-for="item in visibleNav" :key="item.to" :to="item.to" :class="{ active: navActive(item) }" @click="menuOpen = false">
          <span class="nav-ico" v-html="item.icon"></span>{{ item.label }}<b v-if="item.badge && notificationCount" class="nav-badge">{{ notificationCount > 99 ? '99+' : notificationCount }}</b>
        </RouterLink>
      </nav>
      <div v-if="sidePlan" class="side-plan">
        <span>{{ sidePlan.label }}</span>
        <b>{{ sidePlan.title }}</b>
        <div class="side-plan-meter"><i :style="{ width: `${sidePlan.percent}%` }"></i></div>
        <small>Day {{ sidePlan.day }} / {{ sidePlan.total }} · {{ sidePlan.percent }}%</small>
      </div>
      <div v-else class="sidebar-note">
        <p>不追赶别人，<br />只让今天留下证据。</p>
      </div>
      <div v-if="auth.loggedIn" class="profile-row">
        <span class="avatar">{{ initials }}</span>
        <RouterLink class="profile-copy" to="/profile" @click="menuOpen = false"><b>{{ auth.user?.name || '学习者' }}</b><small>@{{ auth.user?.username }}</small></RouterLink>
        <button class="text-button" @click="logout">退出</button>
      </div>
      <RouterLink v-else class="button primary wide guest-login" :to="{ path: '/login', query: { next: route.fullPath } }">登录后开始学习</RouterLink>
    </aside>

    <main class="page-shell"><slot /></main>
    <div v-if="menuOpen" class="scrim" @click="menuOpen = false"></div>
  </div>
</template>
