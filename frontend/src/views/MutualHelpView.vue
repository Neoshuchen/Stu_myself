<script setup>
import { computed, onMounted, ref } from 'vue'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const enrollments = ref(null)
const reviews = ref([])
const sessions = ref([])
const contributions = ref(null)
const buddies = ref([])
const error = ref('')
const busy = ref(false)
const tab = ref('review')
const selectedEnrollment = ref(null)
const buddyForm = ref({ study_time: '', goal: '' })
const reviewForm = ref({ accuracy: true, runnable: true, clarity: true, feedback: '' })
const answering = ref(null)
const answer = ref('')
const question = ref('')
const selectedSession = ref(null)
const openReviews = computed(() => reviews.value.filter((item) => item.status === 'open' && item.role === 'candidate'))
const myReviews = computed(() => reviews.value.filter((item) => item.role !== 'candidate'))

onMounted(load)
async function load() {
  error.value = ''
  try {
    ;[enrollments.value, reviews.value, sessions.value, contributions.value] = await Promise.all([
      api('/enrollments/'), api('/peer-reviews/'), api('/help-sessions/'), api('/contributions/'),
    ])
    selectedEnrollment.value ||= enrollments.value.find((item) => item.status === 'active')?.id || enrollments.value[0]?.id || null
    if (selectedEnrollment.value) buddies.value = await api(`/buddy-profiles/?enrollment=${selectedEnrollment.value}`)
  } catch (err) { error.value = err.message }
}
async function claim(review) {
  busy.value = true
  try { await api(`/peer-reviews/${review.id}/claim/`, { method: 'POST' }); await load() }
  catch (err) { error.value = err.message } finally { busy.value = false }
}
async function submitReview(review) {
  busy.value = true
  try { await api(`/peer-reviews/${review.id}/submit/`, { method: 'POST', body: JSON.stringify(reviewForm.value) }); reviewForm.value.feedback = ''; await load() }
  catch (err) { error.value = err.message } finally { busy.value = false }
}
async function addQuestion(session) {
  busy.value = true
  try { await api(`/help-sessions/${session.id}/questions/`, { method: 'POST', body: JSON.stringify({ question: question.value }) }); question.value = ''; selectedSession.value = null; await load() }
  catch (err) { error.value = err.message } finally { busy.value = false }
}
async function answerQuestion(session, item) {
  busy.value = true
  try { await api(`/help-sessions/${session.id}/questions/${item.id}/answer/`, { method: 'POST', body: JSON.stringify({ answer: answer.value }) }); answer.value = ''; answering.value = null; await load() }
  catch (err) { error.value = err.message } finally { busy.value = false }
}
async function publishBuddy() {
  busy.value = true
  try {
    await api('/buddy-profiles/', { method: 'POST', body: JSON.stringify({ enrollment: selectedEnrollment.value, ...buddyForm.value, active: true }) })
    buddies.value = await api(`/buddy-profiles/?enrollment=${selectedEnrollment.value}`)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
async function enrollmentChanged() { buddies.value = selectedEnrollment.value ? await api(`/buddy-profiles/?enrollment=${selectedEnrollment.value}`) : [] }
</script>

<template>
  <AppShell>
    <LoadingState v-if="!enrollments && !error" />
    <div v-else class="page-enter mutual-page">
      <header class="community-hero mutual-hero"><div><span class="eyebrow">LEARN TOGETHER</span><h1>让学习者真正帮助学习者</h1><p>检查一份真实成果，回答一个具体问题，或找到与你进度相近的人一起推进。</p></div><div v-if="contributions" class="contribution-total"><strong>{{ contributions.total }}</strong><span>次公益贡献</span></div></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <nav class="mutual-tabs"><button :class="{ active: tab === 'review' }" @click="tab = 'review'">同伴互评</button><button :class="{ active: tab === 'help' }" @click="tab = 'help'">公开答疑</button><button :class="{ active: tab === 'buddy' }" @click="tab = 'buddy'">学习搭子</button><button :class="{ active: tab === 'contribution' }" @click="tab = 'contribution'">我的贡献</button></nav>

      <section v-if="tab === 'review'" class="mutual-grid">
        <div><div class="section-title"><h2>等待领取</h2><span>{{ openReviews.length }}</span></div><article v-for="item in openReviews" :key="item.id" class="panel help-card"><span class="eyebrow">{{ item.plan_title }} · DAY {{ item.day_number }}</span><h3>{{ item.day_title }}</h3><p>{{ item.evidence.length }} 项学习证据等待检查</p><button class="button secondary" :disabled="busy" @click="claim(item)">领取互评</button></article><p v-if="!openReviews.length" class="no-gaps">当前没有可领取的互评任务。</p></div>
        <div><div class="section-title"><h2>我的互评</h2></div><article v-for="item in myReviews" :key="item.id" class="panel help-card"><span class="eyebrow">{{ item.plan_title }} · DAY {{ item.day_number }}</span><h3>{{ item.day_title }}</h3><div v-if="item.status === 'claimed' && item.role === 'reviewer'" class="peer-form"><label><input v-model="reviewForm.accuracy" type="checkbox" /> 结论准确</label><label><input v-model="reviewForm.runnable" type="checkbox" /> 证据可复现</label><label><input v-model="reviewForm.clarity" type="checkbox" /> 表达清楚</label><textarea v-model.trim="reviewForm.feedback" rows="3" placeholder="写下一个具体优点和一个改进建议"></textarea><button class="button primary" @click="submitReview(item)">提交互评</button></div><p v-else>{{ item.feedback || (item.role === 'requester' ? '等待同路线学习者领取并完成评审。' : '评审已经完成。') }}</p></article></div>
      </section>

      <section v-if="tab === 'help'" class="session-list"><article v-for="session in sessions" :key="session.id" class="panel session-card"><header><div><span class="eyebrow">{{ session.plan_title || '全站公开答疑' }}</span><h2>{{ session.title }}</h2><p>{{ session.description }}</p></div><small>{{ new Date(session.deadline).toLocaleString('zh-CN') }} 截止</small></header><div class="question-list"><article v-for="item in session.questions" :key="item.id"><b>{{ item.author_name || '学习者' }}</b><p>{{ item.question }}</p><blockquote v-if="item.answer">{{ item.answer }}<small>— {{ item.answered_by_name || '志愿者' }}</small></blockquote><button v-else class="text-action" @click="answering = item.id">我来回答</button><form v-if="answering === item.id" @submit.prevent="answerQuestion(session, item)"><textarea v-model.trim="answer" required rows="3" placeholder="给出可验证、可执行的回答"></textarea><button class="button secondary">提交回答</button></form></article></div><form v-if="session.status === 'open'" class="ask-form" @submit.prevent="addQuestion(session)"><textarea v-model.trim="question" required rows="2" :placeholder="selectedSession === session.id ? '描述问题、已尝试的方法和失败证据' : '向本场答疑提交一个具体问题'" @focus="selectedSession = session.id"></textarea><button class="button ghost">提交问题</button></form></article><p v-if="!sessions.length" class="empty-state">当前还没有公开答疑场次，管理员可以在审核页面创建。</p></section>

      <section v-if="tab === 'buddy'" class="buddy-layout"><form class="panel buddy-form" @submit.prevent="publishBuddy"><h2>开启同进度匹配</h2><p>仅展示同路线且进度相差不超过 3 天的学习者，不公开联系方式。</p><label>学习路线<select v-model="selectedEnrollment" required @change="enrollmentChanged"><option v-for="item in enrollments" :key="item.id" :value="item.id">{{ item.plan.title }} · Day {{ item.current_day }}</option></select></label><label>通常学习时间<input v-model.trim="buddyForm.study_time" required maxlength="80" placeholder="例如：工作日 20:00 后" /></label><label>希望怎样互助<input v-model.trim="buddyForm.goal" required maxlength="240" placeholder="例如：每周互看一次代码和进度" /></label><button class="button primary">发布匹配信息</button></form><div><div class="section-title"><h2>进度相近的学习者</h2></div><article v-for="item in buddies" :key="item.id" class="panel buddy-card"><span class="community-avatar">{{ (item.name || item.username).slice(0, 1) }}</span><div><h3>{{ item.name || item.username }}</h3><p>{{ item.plan_title }} · Day {{ item.current_day }}</p><b>{{ item.study_time }}</b><small>{{ item.goal }}</small></div></article><p v-if="!buddies.length" class="no-gaps">暂时没有进度相近的学习者，你的发布会让后来者找到你。</p></div></section>

      <section v-if="tab === 'contribution'" class="contribution-section"><div class="insight-summary"><article><strong>{{ contributions.total }}</strong><span>全部贡献</span></article><article><strong>{{ contributions.counts.course }}</strong><span>课程共建</span></article><article><strong>{{ contributions.counts.review }}</strong><span>同伴互评</span></article><article><strong>{{ contributions.counts.answer }}</strong><span>志愿答疑</span></article></div><article v-for="item in contributions.items" :key="item.id" class="panel contribution-row"><span>{{ { course: '课程共建', review: '同伴互评', answer: '志愿答疑' }[item.kind] }}</span><div><b>{{ item.title }}</b><p>{{ item.detail }}</p></div><small>{{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</small></article><p v-if="!contributions.items.length" class="no-gaps">帮助别人完成一次可验证的学习，你的第一条公益贡献就会出现在这里。</p></section>
    </div>
  </AppShell>
</template>
