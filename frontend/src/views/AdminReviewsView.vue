<script setup>
import { computed, onMounted, ref } from 'vue'

import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import DayEditor from '../components/DayEditor.vue'
import LoadingState from '../components/LoadingState.vue'

const plans = ref(null)
const selected = ref(null)
const note = ref('')
const error = ref('')
const notice = ref('')
const busy = ref(false)
const reports = ref([])
const suggestions = ref([])
const users = ref([])
const userQuery = ref('')
const allPlans = ref([])
const managed = ref(null)
const editing = ref(null)
const editForm = ref({ title: '', subtitle: '', summary: '', audience: '' })
const sessionForm = ref({ title: '', description: '', deadline: '', plan: null })
const visibleUsers = computed(() => {
  const query = userQuery.value.trim().toLowerCase()
  if (!query) return users.value
  return users.value.filter((user) => [user.username, user.email, user.name].some((value) => value?.toLowerCase().includes(query)))
})
const activeUserCount = computed(() => users.value.filter((user) => user.is_active).length)
const pendingSuggestions = computed(() => suggestions.value.filter((item) => item.status === 'pending'))

// 管理内容按类型分栏，避免所有区块堆在一页里翻找。
const tab = ref('queue')
const TABS = [
  { key: 'queue', label: '待审核路线', count: () => plans.value?.length || 0 },
  { key: 'plans', label: '全部路线', count: () => allPlans.value.length },
  { key: 'users', label: '用户管理', count: () => users.value.length },
  { key: 'reports', label: '社区举报', count: () => reports.value.length },
  { key: 'suggestions', label: '课程共建', count: () => pendingSuggestions.value.length },
  { key: 'sessions', label: '公开答疑', count: () => null },
]

onMounted(load)

async function load() {
  try {
    ;[plans.value, reports.value, suggestions.value, users.value, allPlans.value] = await Promise.all([api('/admin/plan-reviews/'), api('/community/reports/'), api('/course-suggestions/'), api('/admin/users/'), api('/admin/plan-reviews/?scope=all')])
    selected.value = plans.value[0] || null
  } catch (err) { error.value = err.message }
}

// 管理端的路线管理：任何路线（含系统路线、草稿、未发布）都能展开逐日内容并改名、下架或删除。
async function manage(plan) {
  if (managed.value?.id === plan.id) return (managed.value = null)
  managed.value = plan
  editForm.value = { title: plan.title, subtitle: plan.subtitle, summary: plan.summary, audience: plan.audience }
  if (plan.days) return
  try {
    const detail = await api(`/admin/plan-reviews/${plan.slug}/`)
    Object.assign(plan, detail)
  } catch (err) { error.value = err.message }
}

async function savePlan() {
  busy.value = true
  error.value = ''
  try {
    const updated = await api(`/admin/plan-reviews/${managed.value.slug}/`, { method: 'PATCH', body: JSON.stringify(editForm.value) })
    Object.assign(managed.value, updated)
    replacePlan(updated)
    notice.value = '路线信息已更新'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function togglePublished(plan) {
  busy.value = true
  error.value = ''
  try {
    const updated = await api(`/admin/plan-reviews/${plan.slug}/`, { method: 'PATCH', body: JSON.stringify({ is_published: !plan.is_published }) })
    Object.assign(plan, updated)
    notice.value = updated.is_published ? '路线已重新公开' : '路线已下架，已加入的学习者不受影响'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function deletePlan(plan, confirmed = false) {
  if (!confirmed && !confirm(`确认删除“${plan.title}”？\n\n路线的全部学习日、学习进度和证据都会一并永久删除。`)) return
  busy.value = true
  error.value = ''
  try {
    await api(`/admin/plan-reviews/${plan.slug}/${confirmed ? '?confirm=1' : ''}`, { method: 'DELETE' })
    allPlans.value = allPlans.value.filter((item) => item.id !== plan.id)
    plans.value = plans.value.filter((item) => item.id !== plan.id)
    if (managed.value?.id === plan.id) managed.value = null
    if (selected.value?.id === plan.id) selected.value = plans.value[0] || null
    notice.value = '路线已删除'
  } catch (err) {
    // 还有学习者时后端返回 409，必须再确认一次才真正删除。
    if (err.payload?.learner_count && confirm(`${err.message}\n\n仍然要删除吗？`)) return deletePlan(plan, true)
    error.value = err.message
  } finally { busy.value = false }
}

function openDay(plan, dayNumber) {
  editing.value = { slug: plan.slug, title: plan.title, day_number: dayNumber, plan }
}

// 正文保存后同步列表里的摘要，免得收起再展开看到旧标题。
function daySaved(day) {
  const row = editing.value?.plan.days?.find((item) => item.day_number === day.day_number)
  if (row) Object.assign(row, day)
  notice.value = `Day ${day.day_number} 正文已更新`
}

function replacePlan(updated) {
  for (const list of [allPlans.value, plans.value]) {
    const item = list.find((entry) => entry.id === updated.id)
    if (item) Object.assign(item, updated)
  }
}

function formatDate(value) {
  return value ? new Date(value).toLocaleString('zh-CN', { dateStyle: 'short', timeStyle: 'short' }) : '暂无记录'
}

async function toggleUser(user) {
  busy.value = true
  error.value = ''
  try {
    const updated = await api(`/admin/users/${user.id}/set-active/`, {
      method: 'POST', body: JSON.stringify({ is_active: !user.is_active }),
    })
    Object.assign(user, updated)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

// 删除用户是不可撤销的级联删除：报名、进度、证据、社区内容全部一起消失。
async function deleteUser(user) {
  const scope = `${user.enrollment_count} 条学习路线、完成 ${user.completed_days} 天的记录`
  if (!confirm(`确认永久删除账号“${user.name}”（@${user.username}）？\n\n${scope}、上传的证据附件以及他的帖子和评论都会被一并删除，无法恢复。\n\n只想阻止登录请改用「停用账号」。`)) return
  busy.value = true
  error.value = ''
  try {
    const result = await api(`/admin/users/${user.id}/`, { method: 'DELETE' })
    users.value = users.value.filter((item) => item.id !== user.id)
    notice.value = result?.detail || '账号已删除'
    // 他创建的路线可能被连带删除或转为“系统”作者，列表需要重新拉一次。
    allPlans.value = await api('/admin/plan-reviews/?scope=all')
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function reviewSuggestion(item, action) {
  busy.value = true
  try {
    const review_note = action === 'reject' ? prompt('未采纳原因（可选）') || '' : ''
    await api(`/course-suggestions/${item.id}/${action}/`, { method: 'POST', body: JSON.stringify({ review_note }) })
    suggestions.value = suggestions.value.filter((suggestion) => suggestion.id !== item.id)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function createSession() {
  busy.value = true
  try {
    await api('/help-sessions/', { method: 'POST', body: JSON.stringify({ ...sessionForm.value, deadline: new Date(sessionForm.value.deadline).toISOString() }) })
    sessionForm.value = { title: '', description: '', deadline: '', plan: null }
    notice.value = '答疑场次已发布'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function handleReport(report, removeContent = false) {
  busy.value = true
  error.value = ''
  try {
    if (removeContent) {
      const kind = report.post ? 'posts' : 'comments'
      await api(`/community/${kind}/${report.post || report.comment}/`, { method: 'DELETE' })
      reports.value = reports.value.filter((item) => item.id !== report.id)
    } else {
      await api(`/community/reports/${report.id}/`, { method: 'PATCH', body: JSON.stringify({ status: 'resolved' }) })
      reports.value = reports.value.filter((item) => item.id !== report.id)
    }
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function review(action) {
  if (!selected.value) return
  busy.value = true
  error.value = ''
  try {
    await api(`/admin/plan-reviews/${selected.value.slug}/${action}/`, {
      method: 'POST',
      body: JSON.stringify(action === 'reject' ? { review_note: note.value } : {}),
    })
    plans.value = plans.value.filter((plan) => plan.id !== selected.value.id)
    selected.value = plans.value[0] || null
    note.value = ''
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!plans && !error" />
    <div v-else class="page-enter admin-reviews">
      <header class="page-heading compact">
        <div><span class="eyebrow">ADMIN CENTER</span><h1>管理中心</h1><p>集中查看用户学习状态，并处理路线、共建内容和社区审核。</p></div>
        <span class="review-count">{{ plans?.length || 0 }} 条待审核</span>
      </header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <p v-if="notice" class="notice success">{{ notice }}</p>
      <nav class="mutual-tabs">
        <button v-for="item in TABS" :key="item.key" :class="{ active: tab === item.key }" @click="tab = item.key">
          {{ item.label }}<template v-if="item.count() !== null"> · {{ item.count() }}</template>
        </button>
      </nav>
      <section v-if="tab === 'queue' && selected" class="review-layout">
        <aside class="review-queue panel">
          <button v-for="plan in plans" :key="plan.id" :class="{ active: selected.id === plan.id }" @click="selected = plan; note = ''">
            <small>{{ plan.creator_name }} · {{ plan.total_days }} 天</small><b>{{ plan.title }}</b><span>{{ plan.summary }}</span>
          </button>
        </aside>
        <article class="review-content panel">
          <header><span class="card-kicker">{{ selected.subtitle || '用户自定义路线' }}</span><h2>{{ selected.title }}</h2><p>{{ selected.summary }}</p><small>适合：{{ selected.audience || '未填写' }}</small></header>
          <div class="review-days">
            <details v-for="day in selected.days" :key="day.day_number" :open="day.day_number === 1">
              <summary><span>Day {{ day.day_number }}</span><b>{{ day.title }}</b><i>＋</i></summary>
              <div><p><strong>知识点</strong>{{ day.core_knowledge }}</p><p><strong>实践任务</strong>{{ day.hands_on_task }}</p><p><strong>验收标准</strong>{{ day.acceptance_criteria.join('；') }}</p></div>
            </details>
          </div>
          <footer class="review-actions">
            <textarea v-model="note" rows="2" placeholder="退回时填写具体修改意见"></textarea>
            <button class="button secondary" :disabled="busy" @click="review('reject')">退回修改</button>
            <button class="button primary" :disabled="busy" @click="review('approve')">审核通过</button>
          </footer>
        </article>
      </section>
      <section v-else-if="tab === 'queue'" class="empty-state"><div class="empty-orbit">✓</div><h2>待审核路线已清空</h2><p>目前没有用户提交的新路线。</p><RouterLink class="button primary" to="/dashboard">返回今日学习</RouterLink></section>
      <section v-if="tab === 'plans'" class="moderation-section">
        <div class="section-title"><div><h2>全部学习路线</h2><p>包含系统课程、用户草稿和未发布路线。可查看每一天的完整正文，并改名、下架或删除。</p></div><span class="review-count">{{ allPlans.length }} 条路线</span></div>
        <article v-for="plan in allPlans" :key="plan.id" class="panel admin-plan-row">
          <div class="admin-plan-head">
            <div><span class="eyebrow">{{ plan.creator_name }} · {{ plan.total_days }} 天 · {{ plan.learner_count }} 人在学</span><h3>{{ plan.title }}</h3><p>{{ plan.summary }}</p></div>
            <div class="admin-plan-tags">
              <span class="review-badge" :class="plan.review_status">{{ { draft: '草稿', pending: '待审核', approved: '已通过', rejected: '已退回' }[plan.review_status] }}</span>
              <span class="review-badge" :class="plan.is_published ? 'approved' : 'rejected'">{{ plan.is_published ? '已公开' : '未公开' }}</span>
            </div>
            <div class="button-row">
              <button class="button ghost" @click="manage(plan)">{{ managed?.id === plan.id ? '收起' : '管理内容' }}</button>
              <button class="button ghost" :disabled="busy" @click="togglePublished(plan)">{{ plan.is_published ? '下架' : '公开' }}</button>
              <button class="button danger-button" :disabled="busy" @click="deletePlan(plan)">删除</button>
            </div>
          </div>
          <div v-if="managed?.id === plan.id" class="admin-plan-body">
            <form class="admin-plan-form" @submit.prevent="savePlan">
              <label>路线名称<input v-model.trim="editForm.title" required maxlength="160" /></label>
              <label>副标题<input v-model.trim="editForm.subtitle" maxlength="200" /></label>
              <label>适合谁<input v-model.trim="editForm.audience" maxlength="240" /></label>
              <label class="full">简介<textarea v-model.trim="editForm.summary" rows="2"></textarea></label>
              <button class="button secondary" :disabled="busy">保存路线信息</button>
              <small>审核状态请用上方审核队列的通过/退回操作；每一天的正文和知识点点开「查看并编辑正文」直接改。</small>
            </form>
            <LoadingState v-if="!plan.days" />
            <div v-else class="review-days">
              <details v-for="day in plan.days" :key="day.day_number">
                <summary><span>Day {{ day.day_number }}</span><b>{{ day.title }}</b><i>＋</i></summary>
                <div>
                  <p><strong>知识点</strong>{{ day.core_knowledge }}</p>
                  <p><strong>实践任务</strong>{{ day.hands_on_task }}</p>
                  <p><strong>验收标准</strong>{{ day.acceptance_criteria.join('；') }}</p>
                  <button class="text-action" @click="openDay(plan, day.day_number)">查看并编辑正文</button>
                </div>
              </details>
            </div>
          </div>
        </article>
      </section>
      <section v-if="tab === 'users'" class="moderation-section">
        <div class="section-title"><div><h2>用户管理</h2><p>查看账号与学习活跃度；停用后该用户将无法继续登录，删除会连带清除他的全部学习与社区数据。</p></div><span class="review-count">{{ activeUserCount }} / {{ users.length }} 个活跃账号</span></div>
        <div class="panel user-admin-panel">
          <input v-model.trim="userQuery" type="search" placeholder="搜索用户名、昵称或邮箱" aria-label="搜索用户" />
          <div class="user-list">
            <article v-for="user in visibleUsers" :key="user.id" class="user-row">
              <div class="user-identity"><b>{{ user.name }}</b><span>@{{ user.username }} · {{ user.email || '未填写邮箱' }}</span></div>
              <div><small>加入时间</small><span>{{ formatDate(user.date_joined) }}</span></div>
              <div><small>最近学习</small><span>{{ formatDate(user.last_studied_at) }}</span></div>
              <div><small>学习数据</small><span>{{ user.enrollment_count }} 条路线 · 完成 {{ user.completed_days }} 天</span></div>
              <span class="review-badge" :class="user.is_active ? 'approved' : 'rejected'">{{ user.is_staff ? '管理员 · ' : '' }}{{ user.is_active ? '正常' : '已停用' }}</span>
              <div class="button-row">
                <button class="button ghost" :disabled="busy || user.id === auth.user?.id" @click="toggleUser(user)">{{ user.is_active ? '停用账号' : '恢复账号' }}</button>
                <button v-if="!user.is_staff" class="button danger-button" :disabled="busy" @click="deleteUser(user)">删除账号</button>
              </div>
            </article>
            <p v-if="!visibleUsers.length" class="empty-copy">没有匹配的用户。</p>
          </div>
        </div>
      </section>
      <section v-if="tab === 'reports'" class="moderation-section">
        <div class="section-title"><h2>社区举报</h2><span class="review-count">{{ reports.length }} 条待处理</span></div>
        <article v-for="report in reports" :key="report.id" class="panel report-card"><div><b>{{ report.target_title }} · {{ report.target_author }}</b><p>{{ report.target_excerpt }}</p><small>举报原因：{{ report.reason }}</small></div><button class="button ghost" :disabled="busy" @click="handleReport(report)">保留内容</button><button class="button secondary" :disabled="busy" @click="handleReport(report, true)">删除内容</button></article>
        <p v-if="!reports.length" class="panel empty-copy">没有待处理的举报。</p>
      </section>
      <section v-if="tab === 'suggestions'" class="moderation-section">
        <div class="section-title"><h2>课程共建建议</h2><span class="review-count">{{ pendingSuggestions.length }} 条待审核</span></div>
        <article v-for="item in pendingSuggestions" :key="item.id" class="panel suggestion-card"><div><span class="eyebrow">{{ item.plan_title }} · DAY {{ item.day_number }}</span><h3>{{ item.title }}</h3><p>{{ item.content }}</p></div><button class="button ghost" :disabled="busy" @click="reviewSuggestion(item, 'reject')">不采纳</button><button class="button primary" :disabled="busy" @click="reviewSuggestion(item, 'approve')">采纳进课程</button></article>
        <p v-if="!pendingSuggestions.length" class="panel empty-copy">没有待审核的共建内容。</p>
      </section>
      <section v-if="tab === 'sessions'" class="moderation-section"><div class="section-title"><h2>创建公开答疑</h2></div><form class="panel session-admin-form" @submit.prevent="createSession"><label>场次标题<input v-model.trim="sessionForm.title" required placeholder="例如：本周 Python 异步问题门诊" /></label><label>征集截止时间<input v-model="sessionForm.deadline" required type="datetime-local" /></label><label class="full">说明<textarea v-model.trim="sessionForm.description" rows="3" placeholder="本场重点回答哪些问题？"></textarea></label><button class="button secondary" :disabled="busy">发布答疑场次</button></form></section>

      <DayEditor v-if="editing" :slug="editing.slug" :day-number="editing.day_number" :plan-title="editing.title" @close="editing = null" @saved="daySaved" />
    </div>
  </AppShell>
</template>
