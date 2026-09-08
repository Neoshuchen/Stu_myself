<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { activeRoute } from '../activeRoute'
import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'

const router = useRouter()
const route = useRoute()
const data = ref(null)
const error = ref('')
let loadVersion = 0
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 11) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
})
const dateText = new Intl.DateTimeFormat('zh-CN', { month: 'long', day: 'numeric', weekday: 'long' }).format(new Date())

onMounted(() => load(route.query.enrollment || activeRoute.get()))

async function load(enrollmentId) {
  const version = ++loadVersion
  error.value = ''
  data.value = null
  try {
    const loaded = await api(`/dashboard/${enrollmentId ? `?enrollment=${enrollmentId}` : ''}`)
    if (version !== loadVersion) return
    data.value = loaded
    activeRoute.set(loaded.enrollment?.id)
  } catch (err) {
    if (version !== loadVersion) return
    // 记住的路线可能已经退出或被删除，清掉重新按默认路线加载一次。
    if (enrollmentId) {
      activeRoute.clear()
      return load('')
    }
    error.value = err.message
  }
}

async function enrollmentChanged(event) {
  const enrollmentId = event.target.value
  activeRoute.set(enrollmentId)
  await router.replace({ query: enrollmentId ? { enrollment: enrollmentId } : {} })
  await load(enrollmentId)
}

function openToday() {
  const e = data.value.enrollment
  if (e.status === 'paused') return router.push(`/plans/${e.plan.slug}`)
  router.push(`/learn/${e.id}/${e.current_day}`)
}

function actionLabel() {
  if (data.value.enrollment.status === 'paused') return '去恢复路线'
  if (data.value.enrollment.status === 'completed') return '回顾已完成路线'
  return data.value.current_progress.status === 'not_started' ? '开始今天' : '继续学习'
}

function calendarLabel(item) {
  const date = new Date(`${item.date}T00:00:00`)
  return `${date.getMonth() + 1}月${date.getDate()}日，完成 ${item.count} 个学习日`
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!data && !error" />
    <div v-else-if="error" class="notice error">{{ error }}</div>
    <div v-else class="dashboard page-enter">
      <header class="page-heading">
        <div><span class="eyebrow">{{ dateText }}</span><h1>{{ greeting }}，准备好留下今天的证据了吗？</h1></div>
        <label v-if="data.enrollments?.length" class="route-switcher">当前路线<select :value="data.enrollment?.id" @change="enrollmentChanged"><option v-for="item in data.enrollments" :key="item.id" :value="item.id">{{ item.plan.title }} · Day {{ item.current_day }}{{ item.status === 'paused' ? ' · 已暂停' : item.status === 'completed' ? ' · 已完成' : '' }}</option></select></label>
        <span v-else class="focus-pill"><i></i> 今日专注</span>
      </header>

      <EmptyState v-if="!data.enrollment" title="先选择一条值得走的路" copy="计划会替你保管方向，你只需要完成今天。" action="浏览学习计划" @action="router.push('/plans')" />

      <template v-else>
        <section v-if="data.rescue" class="rescue-card"><div><span class="eyebrow">WELCOME BACK · 离开 {{ data.rescue.days_away }} 天</span><h2>{{ data.rescue.title }}</h2><p>不用补回落下的时间，先恢复与这条路线的联系。</p><ol><li v-for="step in data.rescue.steps" :key="step">{{ step }}</li></ol></div><button class="button light" @click="openToday">开始回归任务</button></section>
        <section class="today-card" :style="{ '--accent-a': data.enrollment.plan.accent_start, '--accent-b': data.enrollment.plan.accent_end }">
          <div class="today-copy">
            <span class="card-kicker">DAY {{ data.current_progress.day.day_number }} · 第 {{ data.current_progress.day.week_number }} 周</span>
            <h2>{{ data.current_progress.day.title }}</h2>
            <p>{{ data.current_progress.day.hands_on_task }}</p>
            <p v-if="data.current_progress.resume_note">上次留给自己的提示：{{ data.current_progress.resume_note }}</p>
            <div class="meta-row"><span>{{ data.current_progress.day.estimated_minutes }} 分钟</span><span>{{ data.current_progress.day.week_title }}</span></div>
            <button class="button light" @click="openToday">{{ actionLabel() }}</button>
          </div>
          <div class="progress-orbit" :style="{ '--progress': `${data.enrollment.progress_percent * 3.6}deg` }">
            <div><strong>{{ data.enrollment.progress_percent }}%</strong><span>总进度</span></div>
          </div>
        </section>

        <section class="stats-grid">
          <article><svg viewBox="0 0 24 24" fill="none"><path d="M4 12.5l5 5L20 6.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg><strong>{{ data.stats.completed_days }}</strong><p>完成天数</p></article>
          <article><svg viewBox="0 0 24 24" fill="none"><path d="M12 3s5.5 4.2 5.5 9.3a5.5 5.5 0 0 1-11 0c0-2.1 1.1-3.7 2.2-4.8.4 1.6 1.3 2.3 2.3 2.3-.6-1.8 0-4.8 1-6.8z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg><strong>{{ data.stats.streak }} 天</strong><p>连续学习</p></article>
          <article><svg viewBox="0 0 24 24" fill="none"><path d="M2.5 5.2c3.2-1.6 6.6-1.5 9.5.5 2.9-2 6.3-2.1 9.5-.5v13.6c-3.2-1.6-6.6-1.5-9.5.5-2.9-2-6.3-2.1-9.5-.5z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M12 5.7v13.6" stroke="currentColor" stroke-width="1.8"/></svg><strong>{{ data.stats.evidence_count }}</strong><p>学习证据</p></article>
          <article><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.5" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/></svg><strong>{{ data.stats.open_gaps }}</strong><p>待补缺口</p></article>
        </section>

        <section class="panel activity-calendar">
          <div class="section-title"><div><span class="eyebrow">REAL ACTIVITY</span><h2>最近 28 天学习日历</h2></div><p>本周活跃 {{ data.activity.this_week_active_days }} 天 · 最长连续 {{ data.activity.longest_streak }} 天</p></div>
          <div class="calendar-grid" aria-label="最近28天学习完成情况"><i v-for="item in data.activity.calendar" :key="item.date" :class="{ active: item.count, strong: item.count > 1 }" :title="calendarLabel(item)" :aria-label="calendarLabel(item)"></i></div>
          <div class="calendar-legend"><span>少</span><i></i><i class="active"></i><i class="strong"></i><span>多</span></div>
        </section>

        <div class="dashboard-columns">
          <section class="panel">
            <div class="section-title"><h2>接下来的节奏</h2><RouterLink :to="{ path: '/journey', query: { enrollment: data.enrollment.id } }">查看全路径</RouterLink></div>
            <div class="upcoming-list">
              <div class="upcoming current"><span>今天</span><div><b>{{ data.current_progress.day.title }}</b><small>{{ data.current_progress.day.week_title }}</small></div><i></i></div>
              <div v-for="item in data.upcoming" :key="item.day_number" class="upcoming"><span>Day {{ item.day_number }}</span><div><b>{{ item.title }}</b><small>{{ item.core_knowledge || item.week_title }}</small></div><i></i></div>
            </div>
            <p v-if="data.upcoming?.length" class="upcoming-hint">未来 {{ data.upcoming.length }} 天可以在学习路径中提前查看完整内容，预习不会推进进度。</p>
          </section>
          <aside class="panel ritual-card">
            <h2>今日学习节奏</h2><strong class="ritual-time">15 / 35 / 55 / 15</strong>
            <p>闭卷回忆、官方资料、最小实验、保存证据。</p>
            <div class="ritual-line"><i></i><i></i><i></i><i></i></div>
            <small>不要追求把所有内容看完，先让一个结果可验证。</small>
          </aside>
        </div>
      </template>
    </div>
  </AppShell>
</template>
