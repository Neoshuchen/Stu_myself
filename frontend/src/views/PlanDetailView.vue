<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import { activeRoute } from '../activeRoute'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const route = useRoute()
const router = useRouter()
const plan = ref(null)
const error = ref('')
const busy = ref(false)
const action = ref('')
const feedback = ref({ clarity: 5, practicality: 5, difficulty: 'right', comment: '' })
const feedbackSaved = ref(false)
const weeks = computed(() => {
  const groups = new Map()
  for (const day of plan.value?.days || []) {
    if (!groups.has(day.week_number)) groups.set(day.week_number, { number: day.week_number, title: day.week_title, phase: day.phase, days: [] })
    groups.get(day.week_number).days.push(day)
  }
  return [...groups.values()]
})

onMounted(async () => {
  try {
    plan.value = await api(`/plans/${route.params.slug}/`)
    if (plan.value.my_feedback) feedback.value = { ...feedback.value, ...plan.value.my_feedback }
  } catch (err) { error.value = err.message }
})

/** 加入或继续当前路线；成功进入学习页，失败留在本页提示，无参数和返回值。 */
async function enroll() {
  if (!auth.loggedIn) return router.push({ path: '/login', query: { next: route.fullPath } })
  busy.value = true
  action.value = 'enroll'
  error.value = ''
  try {
    const endpoint = plan.value.owned && plan.value.review_status !== 'approved' ? `/my-plans/${plan.value.slug}/enroll/` : `/plans/${plan.value.slug}/enroll/`
    const enrollment = await api(endpoint, { method: 'POST' })
    router.push(`/learn/${enrollment.id}/${enrollment.current_day}`)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 提交路线审核并刷新审核状态，无参数和返回值。 */
async function submitReview() {
  busy.value = true
  action.value = 'review'
  error.value = ''
  try { plan.value = await api(`/my-plans/${plan.value.slug}/submit/`, { method: 'POST' }) }
  catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 保存当前评分和建议，失败保留输入，无参数和返回值。 */
async function saveFeedback() {
  busy.value = true
  action.value = 'feedback'
  error.value = ''
  feedbackSaved.value = false
  try {
    const saved = await api(`/plans/${plan.value.slug}/feedback/`, { method: 'POST', body: JSON.stringify(feedback.value) })
    plan.value.my_feedback = saved
    feedbackSaved.value = true
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 确认版本名称后复制路线并进入编辑页，无参数和返回值。 */
async function forkPlan() {
  if (!auth.loggedIn) return router.push({ path: '/login', query: { next: route.fullPath } })
  const title = prompt('为你的版本起一个名字', `${plan.value.title} · 我的版本`)?.trim()
  if (!title) return
  const forkNote = prompt('这个版本准备做哪些调整？（可选）')?.trim() || ''
  busy.value = true
  action.value = 'fork'
  error.value = ''
  try {
    const fork = await api(`/plans/${plan.value.slug}/fork/`, { method: 'POST', body: JSON.stringify({ title, fork_note: forkNote }) })
    router.push(`/plans/${fork.slug}/edit`)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 确认后退出当前路线，保留学习记录并更新页面，无参数和返回值。 */
async function withdraw() {
  const enrollmentId = plan.value.my_enrollment?.id
  if (!enrollmentId) return
  if (!confirm(`确认退出“${plan.value.title}”？\n\n已完成的学习进度、证据和缺口记录都会保留，只是这条路线不再出现在你的学习面和小组里。之后重新加入会回到 Day ${plan.value.my_enrollment.current_day}。`)) return
  busy.value = true
  action.value = 'withdraw'
  error.value = ''
  try {
    await api(`/enrollments/${enrollmentId}/`, { method: 'DELETE' })
    if (activeRoute.get() === String(enrollmentId)) activeRoute.clear()
    plan.value = await api(`/plans/${plan.value.slug}/`)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 确认后删除本人未发布路线，成功返回个人页，无参数和返回值。 */
async function removePlan() {
  if (!confirm(`确认删除“${plan.value.title}”？\n\n该路线及相关学习进度、证据和讨论将永久删除，无法恢复。`)) return
  busy.value = true
  action.value = 'delete'
  error.value = ''
  try {
    await api(`/my-plans/${plan.value.slug}/`, { method: 'DELETE' })
    router.push('/profile')
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!plan && !error" />
    <p v-else-if="error && !plan" class="notice error" role="alert">{{ error }}</p>
    <div v-else class="page-enter">
      <section class="plan-hero" :style="{ '--accent-a': plan.accent_start, '--accent-b': plan.accent_end }">
        <div><span class="card-kicker">{{ plan.subtitle }}</span><h1>{{ plan.title }}</h1><p>{{ plan.summary }}</p>
          <div class="meta-row"><span>{{ plan.estimated_weeks }} 周</span><span>{{ plan.total_days }} 个学习日</span><span>以实践证据验收</span></div>
          <div class="button-row"><button class="button light" :disabled="busy" @click="enroll">{{ busy && action === 'enroll' ? (plan.enrolled ? '正在打开…' : '正在加入…') : plan.enrolled ? '继续这条路径' : plan.owned ? '加入我的学习路径' : '加入学习计划' }}</button><RouterLink v-if="plan.enrolled" class="button hero-ghost" :to="`/plans/${plan.slug}/community`">进入学习小组</RouterLink><button v-if="plan.enrolled" class="button hero-ghost" :disabled="busy" @click="withdraw">{{ busy && action === 'withdraw' ? '正在退出…' : '退出这条路线' }}</button><button v-if="plan.review_status === 'approved'" class="button hero-ghost" :disabled="busy" @click="forkPlan">{{ busy && action === 'fork' ? '正在复制…' : 'Fork 这条路线' }}</button><RouterLink v-if="plan.editable" class="button hero-ghost" :to="`/plans/${plan.slug}/edit`">编辑路线</RouterLink><button v-if="plan.owned && ['draft', 'rejected'].includes(plan.review_status)" class="button hero-ghost" :disabled="busy" @click="submitReview">{{ busy && action === 'review' ? '正在提交…' : '提交审核' }}</button><button v-if="plan.owned && !plan.is_published" class="button hero-danger" :disabled="busy" @click="removePlan">{{ busy && action === 'delete' ? '正在删除…' : '删除路线' }}</button></div>
        </div>
      </section>
      <p v-if="error && action !== 'feedback'" class="notice error" role="alert">{{ error }}</p>
      <p v-if="plan.owned" :class="['review-notice', plan.review_status]">{{ { draft: '这是你的草稿。完善后可提交管理员审核，也可以直接加入自己的学习路径。', pending: '路线已提交审核，审核期间不能修改。', approved: '路线已通过审核，并已发布到系统学习计划。', rejected: `管理员已退回修改${plan.review_note ? `：${plan.review_note}` : '。'}` }[plan.review_status] }}</p>
      <p v-if="plan.forked_from" class="fork-origin">源自 <RouterLink :to="`/plans/${plan.forked_from.slug}`">{{ plan.forked_from.title }}</RouterLink><span v-if="plan.fork_note"> · {{ plan.fork_note }}</span></p>
      <section class="plan-detail-grid">
        <div>
          <div class="section-title"><h2>{{ plan.estimated_weeks }}周路径一览</h2></div>
          <div class="week-list">
            <details v-for="week in weeks" :key="week.number" :open="week.number === 1">
              <summary><span>W{{ String(week.number).padStart(2, '0') }}</span><div><b>{{ week.title }}</b><small>{{ week.phase }}</small></div><i>＋</i></summary>
              <ol><li v-for="day in week.days" :key="day.day_number"><span>Day {{ day.day_number }}</span>{{ day.title }}<small>{{ day.estimated_minutes }} min</small></li></ol>
            </details>
          </div>
        </div>
        <aside class="panel sticky-panel"><h2>适合谁</h2><h3>{{ plan.audience }}</h3><hr /><h2>完成方式</h2><ul class="check-list"><li>每天完成一个最小实验</li><li>提交代码、测试或报告证据</li><li>通过明确验收项后进入下一天</li><li>每周记录具体知识缺口</li></ul></aside>
      </section>
      <section v-if="plan.enrolled" class="panel plan-feedback">
        <p v-if="error && action === 'feedback'" class="notice error" role="alert">{{ error }}</p>
        <header><div><span class="eyebrow">ROUTE FEEDBACK</span><h2>这条路线真的好学吗？</h2><p>反馈会帮助后来者选择路线，也帮助维护者发现需要调整的地方。</p></div><div v-if="plan.feedback_summary.count" class="feedback-score"><strong>{{ plan.feedback_summary.clarity }}</strong><span>清晰度 · {{ plan.feedback_summary.count }} 人反馈</span></div></header>
        <form @submit.prevent="saveFeedback"><label>内容清晰度 <span><button v-for="score in 5" :key="score" type="button" :class="{ active: feedback.clarity === score }" @click="feedback.clarity = score">{{ score }}</button></span></label><label>实践有效性 <span><button v-for="score in 5" :key="score" type="button" :class="{ active: feedback.practicality === score }" @click="feedback.practicality = score">{{ score }}</button></span></label><label>难度感受 <select v-model="feedback.difficulty"><option value="easy">偏简单</option><option value="right">刚刚好</option><option value="hard">偏困难</option></select></label><label class="feedback-comment">补充建议<textarea v-model.trim="feedback.comment" rows="3" placeholder="哪一天最难？哪个任务最有帮助？"></textarea></label><button class="button secondary" :disabled="busy">{{ busy && action === 'feedback' ? '正在保存…' : plan.my_feedback ? '更新反馈' : '提交反馈' }}</button><small v-if="feedbackSaved">反馈已保存，谢谢你帮助这条路线变得更好。</small></form>
      </section>
    </div>
  </AppShell>
</template>
