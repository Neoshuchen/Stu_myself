<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const route = useRoute()
const groups = ref(null)
const enrollments = ref([])
const selectedGroupId = ref('')
const dashboard = ref(null)
const challenges = ref([])
const resultCard = ref(null)
const error = ref('')
const notice = ref('')
const busy = ref(false)
const createName = ref('')
const joinCode = ref('')
const gapNotes = reactive({})
const entryForms = reactive({})
const contractForm = ref({ enrollment: '', target_days: 3, note: '' })
const challengeForm = ref({ title: '', description: '', deadline: '' })
const challengeRoles = [
  { value: 'reproduce', label: '复现' },
  { value: 'test', label: '测试' },
  { value: 'explain', label: '讲解' },
  { value: 'review', label: '复核' },
]

const currentMember = computed(() => dashboard.value?.members.find((item) => item.is_current_user))
const currentContract = computed(() => currentMember.value?.contract)
const resultText = computed(() => {
  if (!resultCard.value) return ''
  const card = resultCard.value
  return `${card.user_name} 在 ${card.group_name} 的本周成果：完成 ${card.completed_days} 个学习日，提交 ${card.evidence_count} 份证据，解决 ${card.resolved_gaps} 个知识缺口，完成 ${card.peer_reviews} 次互评、${card.challenges_completed} 次小队挑战，当前连续学习 ${card.current_streak} 天。`
})

onMounted(() => load(route.query.group))

/** 用现有讲解、复现分工准备接力挑战，保留用户设置的截止时间并等待主动发布。 */
function prepareTeachBack() {
  if ((challengeForm.value.title || challengeForm.value.description) && !confirm('用讲解接力模板替换尚未发布的挑战文字？')) return
  challengeForm.value.title = '讲解接力：把一个知识点讲到可复现'
  challengeForm.value.description = '共同主题（请填写）：\n1. 讲解者：用自己的话写约 200 字，说明原理、一个例子和适用边界，提交讲解笔记证据。\n2. 复现者：只按讲解完成一次练习，记录结果及仍不清楚的地方，提交自己的复现证据。\n3. 讲解者：根据反馈修正说明，更新分工证据与结论。\n4. 双方核对修正后的结果，再合并挑战。'
  document.querySelector('.challenge-create').open = true
}

async function load(preferredGroup = '') {
  error.value = ''
  try {
    const [availableGroups, learning] = await Promise.all([api('/study-groups/'), api('/dashboard/')])
    groups.value = availableGroups
    enrollments.value = learning.enrollments || []
    const wanted = String(preferredGroup || selectedGroupId.value)
    selectedGroupId.value = availableGroups.some((item) => String(item.id) === wanted)
      ? wanted
      : String(availableGroups[0]?.id || '')
    if (selectedGroupId.value) await loadDashboard()
  } catch (err) { error.value = err.message }
}

async function loadDashboard() {
  dashboard.value = null
  challenges.value = []
  resultCard.value = null
  if (!selectedGroupId.value) return
  try {
    const [team, challengeList, card] = await Promise.all([
      api(`/study-groups/${selectedGroupId.value}/dashboard/`),
      api(`/team-challenges/?group=${selectedGroupId.value}`),
      api(`/study-groups/${selectedGroupId.value}/result-card/`),
    ])
    dashboard.value = team
    challenges.value = challengeList
    resultCard.value = card
    const contract = dashboard.value.members.find((item) => item.is_current_user)?.contract
    contractForm.value = contract
      ? { enrollment: String(contract.enrollment), target_days: contract.target_days, note: contract.note }
      : { enrollment: String(enrollments.value[0]?.id || ''), target_days: 3, note: '' }
    prepareEntryForms()
  } catch (err) { error.value = err.message }
}

function prepareEntryForms() {
  const currentUserId = currentMember.value?.id
  for (const challenge of challenges.value) {
    const own = challenge.entries.find(item => item.user_id === currentUserId)
    const availableRole = challengeRoles.find(role => !challenge.entries.some(item => item.user_id !== currentUserId && item.role === role.value))
    entryForms[challenge.id] = {
      role: own?.role || availableRole?.value || 'reproduce',
      evidence: String(own?.evidence_id || dashboard.value.evidence_options[0]?.id || ''),
      summary: own?.summary || '',
    }
  }
}

async function createGroup() {
  busy.value = true
  error.value = ''
  try {
    const group = await api('/study-groups/', { method: 'POST', body: JSON.stringify({ name: createName.value }) })
    createName.value = ''
    notice.value = '学习小队已创建。'
    await load(group.id)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function joinGroup() {
  busy.value = true
  error.value = ''
  try {
    const group = await api('/study-groups/join/', { method: 'POST', body: JSON.stringify({ invite_code: joinCode.value }) })
    joinCode.value = ''
    notice.value = `已加入 ${group.name}。`
    await load(group.id)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function saveContract() {
  busy.value = true
  error.value = ''
  const payload = {
    group: Number(selectedGroupId.value),
    enrollment: Number(contractForm.value.enrollment),
    week_start: dashboard.value.week_start,
    target_days: Number(contractForm.value.target_days),
    note: contractForm.value.note,
  }
  try {
    await api(currentContract.value ? `/weekly-contracts/${currentContract.value.id}/` : '/weekly-contracts/', {
      method: currentContract.value ? 'PATCH' : 'POST',
      body: JSON.stringify(payload),
    })
    notice.value = '本周学习契约已保存。'
    await loadDashboard()
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function rotateCode() {
  if (!window.confirm('旧邀请码会立即失效，确定更新吗？')) return
  busy.value = true
  try {
    await api(`/study-groups/${selectedGroupId.value}/rotate-code/`, { method: 'POST' })
    notice.value = '邀请码已更新。'
    await load(selectedGroupId.value)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function verifyGap(gap, approved) {
  busy.value = true
  error.value = ''
  try {
    await api(`/gaps/${gap.id}/verify/`, {
      method: 'POST',
      body: JSON.stringify({ approved, note: gapNotes[gap.id] || '' }),
    })
    notice.value = approved ? '已确认朋友解决了这个缺口。' : '已退回并发送补充说明。'
    await loadDashboard()
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function createChallenge() {
  busy.value = true
  error.value = ''
  try {
    await api('/team-challenges/', {
      method: 'POST',
      body: JSON.stringify({ ...challengeForm.value, group: Number(selectedGroupId.value) }),
    })
    challengeForm.value = { title: '', description: '', deadline: '' }
    notice.value = '协作挑战已发起，朋友会收到通知。'
    await loadDashboard()
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function contribute(challenge) {
  busy.value = true
  error.value = ''
  const form = entryForms[challenge.id]
  try {
    await api(`/team-challenges/${challenge.id}/contribute/`, {
      method: 'POST',
      body: JSON.stringify({ ...form, evidence: Number(form.evidence) }),
    })
    notice.value = '分工与学习证据已加入挑战。'
    await loadDashboard()
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function completeChallenge(challenge) {
  if (!window.confirm('确定合并全部成员的分工并完成这项挑战吗？')) return
  busy.value = true
  error.value = ''
  try {
    await api(`/team-challenges/${challenge.id}/complete/`, { method: 'POST' })
    notice.value = '小队挑战已完成，每位参与者都获得了成长贡献。'
    await loadDashboard()
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

function roleDisabled(challenge, role) {
  return challenge.entries.some(item => item.user_id !== currentMember.value?.id && item.role === role)
}

async function shareResult() {
  try {
    if (navigator.share) await navigator.share({ title: '本周学习成果', text: resultText.value })
    else await navigator.clipboard.writeText(resultText.value)
    notice.value = navigator.share ? '已打开系统分享面板。' : '成果文字已复制。'
  } catch (err) {
    if (err.name !== 'AbortError') window.prompt('复制下面的成果文字', resultText.value)
  }
}

function formatDate(value) {
  return value ? new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric' }).format(new Date(`${value}T00:00:00`)) : '尚未开始'
}

function formatDateTime(value) {
  return value ? new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(value)) : '—'
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="groups === null" />
    <div v-else class="team-page page-enter">
      <header class="page-heading compact">
        <div><span class="eyebrow">STUDY SQUAD</span><h1>和朋友一起把本周走完</h1><p>目标可以不同，但每个人都让本周留下真实进展。</p></div>
        <label v-if="groups.length" class="route-switcher">当前小队<select v-model="selectedGroupId" @change="loadDashboard"><option v-for="group in groups" :key="group.id" :value="String(group.id)">{{ group.name }}</option></select></label>
      </header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <p v-if="notice" class="notice success">{{ notice }}</p>

      <section v-if="!groups.length" class="team-onboarding">
        <article class="panel"><span class="eyebrow">CREATE</span><h2>创建自己的学习小队</h2><p>创建后把邀请码交给朋友即可。</p><form class="form-stack" @submit.prevent="createGroup"><label>小队名称<input v-model.trim="createName" required maxlength="80" placeholder="例如：周末逆向小组" /></label><button class="button primary" :disabled="busy">创建小队</button></form></article>
        <article class="panel"><span class="eyebrow">JOIN</span><h2>加入朋友的小队</h2><p>输入朋友提供的 12 位邀请码。</p><form class="form-stack" @submit.prevent="joinGroup"><label>邀请码<input v-model.trim="joinCode" required maxlength="12" placeholder="例如：A1B2C3D4E5F6" /></label><button class="button secondary" :disabled="busy">加入小队</button></form></article>
      </section>

      <template v-else-if="dashboard">
        <section class="team-hero panel">
          <div><span class="eyebrow">{{ formatDate(dashboard.week_start) }} — {{ formatDate(dashboard.week_end) }}</span><h2>{{ dashboard.group.name }}</h2><p>{{ dashboard.group.member_count }} 位成员正在共享本周目标。</p></div>
          <div v-if="dashboard.group.owned" class="invite-code"><small>朋友邀请码</small><strong>{{ dashboard.group.invite_code }}</strong><button class="text-action" :disabled="busy" @click="rotateCode">更新邀请码</button></div>
        </section>

        <div class="team-columns">
          <section class="panel contract-card">
            <div class="section-title"><div><span class="eyebrow">MY CONTRACT</span><h2>我的本周契约</h2></div></div>
            <form v-if="enrollments.length" class="form-stack" @submit.prevent="saveContract">
              <label>本周路线<select v-model="contractForm.enrollment" required><option v-for="item in enrollments" :key="item.id" :value="String(item.id)">{{ item.plan.title }}</option></select></label>
              <label>计划完成学习日数<input v-model.number="contractForm.target_days" type="number" min="1" max="7" required /></label>
              <label>本周想完成什么<textarea v-model.trim="contractForm.note" maxlength="240" rows="3" placeholder="例如：走完异常处理阶段，并请朋友看一次证据。"></textarea></label>
              <button class="button primary" :disabled="busy">保存本周契约</button>
            </form>
            <p v-else class="muted">先加入一条学习路线，再制定本周目标。</p>
          </section>

          <section class="panel member-board">
            <div class="section-title"><div><span class="eyebrow">WEEKLY BOARD</span><h2>小队本周进度</h2></div></div>
            <article v-for="member in dashboard.members" :key="member.id" class="member-row">
              <span class="avatar">{{ member.name.slice(0, 1) }}</span>
              <div><b>{{ member.name }} <small v-if="member.is_current_user">我</small></b><p v-if="member.contract">{{ member.contract.plan_title }} · {{ member.contract.note || '先完成约定的学习日' }}</p><p v-else>还没有制定本周契约</p><div v-if="member.contract" class="contract-meter"><i :style="{ width: `${Math.min(100, member.completed_days / member.contract.target_days * 100)}%` }"></i></div></div>
              <strong v-if="member.contract">{{ member.completed_days }}/{{ member.contract.target_days }} 天</strong><strong v-else>—</strong>
              <small class="member-streak">连续 {{ member.current_streak }} 天 · 最近 {{ formatDate(member.last_active_date) }}</small>
            </article>
          </section>
        </div>

        <section class="panel gap-verification-board">
          <div class="section-title"><div><span class="eyebrow">FRIEND CHECK</span><h2>等待朋友验证的知识缺口</h2></div><span>{{ dashboard.pending_gaps.length }} 项</span></div>
          <div v-if="dashboard.pending_gaps.length" class="verification-list">
            <article v-for="gap in dashboard.pending_gaps" :key="gap.id">
              <header><span>{{ gap.owner_name }} · {{ gap.plan_title }} Day {{ gap.day_number }}</span><b>{{ gap.title }}</b></header>
              <p>{{ gap.detail }}</p><blockquote>{{ gap.resolution }}</blockquote><small>已附 {{ gap.evidence_count }} 份学习证据</small>
              <div v-if="gap.can_verify" class="verification-actions"><textarea v-model.trim="gapNotes[gap.id]" maxlength="300" rows="2" placeholder="通过可选填；退回时请说明要补充什么。"></textarea><div class="button-row"><button class="button ghost" :disabled="busy" @click="verifyGap(gap, false)">退回补充</button><button class="button primary" :disabled="busy" @click="verifyGap(gap, true)">确认解决</button></div></div>
              <p v-else class="muted">正在等待其他小队成员核对。</p>
            </article>
          </div>
          <p v-else class="muted">现在没有待验证缺口。学习中遇到问题时，可以从每日学习页发起验证。</p>
        </section>

        <section class="panel challenge-board">
          <div class="section-title"><div><span class="eyebrow">CO-OP CHALLENGE</span><h2>小队协作挑战</h2></div><span>{{ challenges.filter(item => item.status === 'open').length }} 项进行中</span></div>
          <p class="muted">不同成员分别复现、测试、讲解或复核，提交已有学习证据后再合并完成。</p>
          <button class="button secondary" :disabled="busy" @click="prepareTeachBack">用讲解接力模板发起</button>
          <details class="challenge-create"><summary>发起一个新挑战</summary><form class="form-stack" @submit.prevent="createChallenge"><label>挑战名称<input v-model.trim="challengeForm.title" required maxlength="160" placeholder="例如：联合排查一次失败实验" /></label><label>共同任务<textarea v-model.trim="challengeForm.description" required rows="3" placeholder="写清目标、失败条件和最终要合并的结论。"></textarea></label><label>截止时间<input v-model="challengeForm.deadline" type="datetime-local" required /></label><button class="button secondary" :disabled="busy">发起挑战</button></form></details>
          <div v-if="challenges.length" class="challenge-list">
            <article v-for="challenge in challenges" :key="challenge.id" :class="{ completed: challenge.status === 'completed' }">
              <header><div><span>{{ challenge.created_by_name }} 发起 · 截止 {{ formatDateTime(challenge.deadline) }}</span><h3>{{ challenge.title }}</h3></div><strong>{{ challenge.status_label }}</strong></header>
              <p>{{ challenge.description }}</p>
              <div class="challenge-entries"><article v-for="entry in challenge.entries" :key="entry.id">
                <b>{{ entry.role_label }} · {{ entry.user_name }}</b><p class="content-body">{{ entry.summary }}</p>
                <details v-if="entry.evidence_detail"><summary>查看证据：{{ entry.evidence_title }}</summary><p class="content-body">{{ entry.evidence_detail.content }}</p>
                  <a v-if="entry.evidence_detail.url" :href="entry.evidence_detail.url" target="_blank" rel="noopener noreferrer">打开证据链接 ↗</a>
                  <a v-if="entry.evidence_detail.attachment_url" :href="entry.evidence_detail.attachment_url" target="_blank" rel="noopener noreferrer">查看附件 {{ entry.evidence_detail.attachment_name }}</a>
                </details><p v-else class="muted">证据已删除，请作者重新提交。</p>
              </article></div>
              <form v-if="challenge.status === 'open' && !challenge.expired && dashboard.evidence_options.length" class="challenge-entry-form" @submit.prevent="contribute(challenge)">
                <p class="challenge-summary muted">提交后，本小队成员可以查看你的过程说明，以及所选证据的正文、链接和附件。</p>
                <label>我的分工<select v-model="entryForms[challenge.id].role" required><option v-for="role in challengeRoles" :key="role.value" :value="role.value" :disabled="roleDisabled(challenge, role.value)">{{ role.label }}{{ roleDisabled(challenge, role.value) ? ' · 已有人承担' : '' }}</option></select></label>
                <label>学习证据<select v-model="entryForms[challenge.id].evidence" required><option v-for="evidence in dashboard.evidence_options" :key="evidence.id" :value="String(evidence.id)">{{ evidence.plan_title }} Day {{ evidence.day_number }} · {{ evidence.title }}</option></select></label>
                <label class="challenge-summary">过程与结论<textarea v-model.trim="entryForms[challenge.id].summary" required rows="2" placeholder="说明你做了什么、发现了什么。"></textarea></label>
                <button class="button secondary" :disabled="busy">{{ challenge.entries.some(item => item.user_id === currentMember?.id) ? '更新我的分工' : '提交分工证据' }}</button>
              </form>
              <p v-else-if="challenge.status === 'open' && !dashboard.evidence_options.length" class="muted">先在每日学习页提交一份真实证据，再回来承担分工。</p>
              <p v-else-if="challenge.expired" class="muted">挑战已截止，保留现有分工记录但不能继续提交。</p>
              <button v-if="challenge.can_complete" class="button primary" :disabled="busy" @click="completeChallenge(challenge)">合并证据并完成挑战</button>
            </article>
          </div>
          <p v-else class="muted">还没有协作挑战。可以从一次需要共同复现的失败实验开始。</p>
        </section>

        <section v-if="resultCard" class="result-card panel">
          <div><span class="eyebrow">WEEKLY RESULT</span><h2>{{ resultCard.user_name }} 的本周成果</h2><p>{{ formatDate(resultCard.week_start) }} — {{ formatDate(resultCard.week_end) }} · {{ resultCard.group_name }}</p><p v-if="resultCard.target_days" :class="resultCard.goal_met ? 'goal-met' : 'muted'">周契约：{{ resultCard.contract_completed_days }}/{{ resultCard.target_days }} 天{{ resultCard.goal_met ? ' · 已兑现' : ' · 继续前进' }}</p></div>
          <div class="result-stats"><span><strong>{{ resultCard.completed_days }}</strong>学习日</span><span><strong>{{ resultCard.evidence_count }}</strong>份证据</span><span><strong>{{ resultCard.resolved_gaps }}</strong>个缺口</span><span><strong>{{ resultCard.peer_reviews }}</strong>次互评</span><span><strong>{{ resultCard.challenges_completed }}</strong>次挑战</span><span><strong>{{ resultCard.current_streak }}</strong>天连续</span></div>
          <button class="button secondary" @click="shareResult">分享成果文字</button>
        </section>

        <details class="panel team-more"><summary>创建或加入其他小队</summary><div class="team-onboarding compact"><form class="form-stack" @submit.prevent="createGroup"><label>新小队名称<input v-model.trim="createName" required maxlength="80" /></label><button class="button secondary" :disabled="busy">创建</button></form><form class="form-stack" @submit.prevent="joinGroup"><label>朋友邀请码<input v-model.trim="joinCode" required maxlength="12" /></label><button class="button secondary" :disabled="busy">加入</button></form></div></details>
      </template>
    </div>
  </AppShell>
</template>
