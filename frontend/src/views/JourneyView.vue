<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { activeRoute } from '../activeRoute'
import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import DayEditor from '../components/DayEditor.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'

const router = useRouter()
const route = useRoute()
const enrollments = ref([])
const enrollment = ref(null)
const days = ref(null)
const error = ref('')
const preview = ref(null)
const previewError = ref('')
const previewDialog = ref(null)
const editing = ref(null)
// 管理员不预习：任何一天都直接进正文编辑器查看或修改。
const isStaff = computed(() => !!auth.user?.is_staff)
let loadVersion = 0
const weeks = computed(() => {
  const groups = new Map()
  for (const day of days.value || []) {
    if (!groups.has(day.week_number)) groups.set(day.week_number, { number: day.week_number, title: day.week_title, days: [] })
    groups.get(day.week_number).days.push(day)
  }
  return [...groups.values()]
})
const phases = computed(() => {
  const groups = new Map()
  for (const day of days.value || []) {
    if (!groups.has(day.phase)) groups.set(day.phase, { name: day.phase, days: [] })
    groups.get(day.phase).days.push(day)
  }
  return [...groups.values()].map((phase) => {
    const completed = phase.days.filter(day => day.status === 'completed').length
    const current = phase.days.some(day => day.day_number === enrollment.value?.current_day)
    return {
      ...phase,
      start: phase.days[0].day_number,
      end: phase.days.at(-1).day_number,
      boss: phase.days.find(day => day.is_boss),
      completed,
      status: completed === phase.days.length ? 'completed' : current ? 'active' : 'pending',
    }
  })
})

onMounted(async () => {
  try {
    const list = await api('/enrollments/')
    enrollments.value = list
    const wanted = route.query.enrollment || activeRoute.get()
    enrollment.value = list.find(item => String(item.id) === String(wanted)) || list.find(item => item.status === 'active') || list[0]
    activeRoute.set(enrollment.value?.id)
    await loadDays()
  } catch (err) { error.value = err.message }
})

async function loadDays() {
  const version = ++loadVersion
  days.value = null
  const loaded = enrollment.value ? await api(`/enrollments/${enrollment.value.id}/days/`) : []
  if (version === loadVersion) days.value = loaded
}

async function enrollmentChanged(event) {
  enrollment.value = enrollments.value.find(item => String(item.id) === event.target.value)
  activeRoute.set(enrollment.value.id)
  await router.replace({ query: { enrollment: enrollment.value.id } })
  await loadDays()
}

function openDay(day) {
  if (isStaff.value && day.day_number > enrollment.value.current_day) {
    return (editing.value = { day_number: day.day_number, plan: enrollment.value.plan })
  }
  if (day.previewable) return openPreview(day)
  if (day.day_number > enrollment.value.current_day) return
  if (enrollment.value.status === 'paused') return router.push(`/plans/${enrollment.value.plan.slug}`)
  router.push(`/learn/${enrollment.value.id}/${day.day_number}`)
}

// 预习是只读的：只取正文，不建进度，也不能在这里提交验收或证据。
async function openPreview(day) {
  preview.value = { day_number: day.day_number, title: day.title, content: null }
  previewError.value = ''
  await nextTick()
  if (!previewDialog.value.open) previewDialog.value.showModal()
  try {
    const data = await api(`/plans/${enrollment.value.plan.slug}/day/?number=${day.day_number}`)
    if (preview.value?.day_number === day.day_number) preview.value.content = data.day
  } catch (err) {
    previewError.value = err.message
  }
}

function closePreview() {
  if (previewDialog.value?.open) previewDialog.value.close()
  preview.value = null
}

// 编辑器里改完标题或时长，直接同步到格子上，不必整页重载。
function daySaved(day) {
  const tile = days.value?.find((item) => item.day_number === day.day_number)
  if (tile) Object.assign(tile, { title: day.title, estimated_minutes: day.estimated_minutes })
}

function jumpToPhase(phase) {
  document.getElementById(`day-${phase.start}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="days === null && !error" />
    <p v-else-if="error" class="notice error">{{ error }}</p>
    <EmptyState v-else-if="!enrollment" title="还没有学习路径" copy="选择一个计划，让每一天都有清晰的下一步。" action="选择计划" @action="router.push('/plans')" />
    <div v-else class="page-enter">
      <header class="page-heading"><div><h1>{{ enrollment.plan.title }}</h1><p>已完成 {{ enrollment.completed_days }} / {{ enrollment.plan.total_days }} 天<span v-if="enrollment.status === 'paused'"> · 路线已暂停，点击学习日将前往恢复</span></p></div><div class="journey-heading-actions"><label v-if="enrollments.length > 1" class="route-switcher">切换路线<select :value="enrollment.id" @change="enrollmentChanged"><option v-for="item in enrollments" :key="item.id" :value="item.id">{{ item.plan.title }} · Day {{ item.current_day }}{{ item.status === 'paused' ? ' · 已暂停' : item.status === 'completed' ? ' · 已完成' : '' }}</option></select></label><div class="percent-badge"><strong>{{ enrollment.progress_percent }}%</strong><span>总进度</span></div></div></header>
      <div class="journey-progress"><i :style="{ width: `${enrollment.progress_percent}%` }"></i></div>
      <section class="phase-map" aria-label="阶段路线地图">
        <button v-for="(phase, index) in phases" :key="phase.name" :class="phase.status" @click="jumpToPhase(phase)">
          <i>{{ phase.status === 'completed' ? '✓' : index + 1 }}</i><span><small>DAY {{ phase.start }}—{{ phase.end }}</small><b>{{ phase.name }}</b><em>{{ phase.completed }}/{{ phase.days.length }} · Boss Day {{ phase.boss?.day_number }}</em></span>
        </button>
      </section>
      <section class="journey-weeks">
        <article v-for="week in weeks" :key="week.number" class="journey-week">
          <header><span>W{{ String(week.number).padStart(2, '0') }}</span><div><h2>{{ week.title }}</h2><p>{{ week.days.filter(d => d.status === 'completed').length }} / {{ week.days.length }} 完成</p></div></header>
          <div class="day-grid">
            <button v-for="day in week.days" :id="`day-${day.day_number}`" :key="day.day_number" :class="['day-tile', day.status, { boss: day.is_boss, locked: day.day_number > enrollment.current_day && !day.previewable, preview: day.previewable && !isStaff }]" :disabled="day.day_number > enrollment.current_day && !day.previewable" @click="openDay(day)">
              <span>{{ String(day.day_number).padStart(2, '0') }}</span><em v-if="day.is_boss" class="boss-mark">BOSS</em><b>{{ day.title }}</b><small>{{ day.previewable && !isStaff ? '可预习' : `${day.estimated_minutes} min` }}</small>
            </button>
          </div>
        </article>
      </section>

      <dialog ref="previewDialog" class="knowledge-dialog" @click.self="closePreview" @close="preview = null">
        <article v-if="preview" class="knowledge-drawer">
          <header>
            <div><span class="eyebrow">预习 · DAY {{ preview.day_number }}</span><h2>{{ preview.title }}</h2><p>提前了解内容，不会开始或推进这一天的学习进度。</p></div>
            <button aria-label="关闭预习" @click="closePreview">×</button>
          </header>
          <div class="knowledge-scroll">
            <p v-if="previewError" class="notice error">{{ previewError }}</p>
            <LoadingState v-else-if="!preview.content" />
            <template v-else>
              <section><span class="detail-label">今天要掌握什么</span><p>{{ preview.content.core_knowledge }}</p></section>
              <section v-for="item in preview.content.knowledge_details" :key="item.name"><span class="detail-label">{{ item.name }}</span><p>{{ item.summary }}</p><p v-if="item.mechanism">{{ item.mechanism }}</p></section>
              <section><span class="detail-label">最终复现任务</span><p>{{ preview.content.hands_on_task }}</p></section>
              <section v-if="preview.content.acceptance_criteria?.length"><span class="detail-label">验收标准</span><ul><li v-for="item in preview.content.acceptance_criteria" :key="item">{{ item }}</li></ul></section>
              <section v-if="preview.content.commands?.length"><span class="detail-label">运行与验证</span><pre v-for="command in preview.content.commands" :key="command"><code>{{ command }}</code></pre></section>
            </template>
          </div>
          <footer><span>预计 {{ preview.content?.estimated_minutes || '—' }} 分钟 · 完成前面的学习日后即可正式开始</span><button class="button secondary" @click="closePreview">知道了</button></footer>
        </article>
      </dialog>

      <DayEditor v-if="editing" :slug="editing.plan.slug" :day-number="editing.day_number" :plan-title="editing.plan.title" @close="editing = null" @saved="daySaved" />
    </div>
  </AppShell>
</template>
