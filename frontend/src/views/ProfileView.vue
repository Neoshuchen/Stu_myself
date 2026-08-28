<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const router = useRouter()
const plans = ref(null)
const profile = ref({ name: auth.user?.name || '', email: auth.user?.email || '', email_code: '' })
const password = ref({ current_password: '', new_password: '', confirm_password: '' })
const busy = ref(false)
const error = ref('')
const notice = ref('')
const sendingCode = ref(false)
const emailChanged = computed(() => profile.value.email.trim().toLowerCase() !== (auth.user?.email || '').trim().toLowerCase())

async function sendEmailCode() {
  error.value = ''
  notice.value = ''
  if (!profile.value.email) {
    error.value = '请先填写新邮箱。'
    return
  }
  sendingCode.value = true
  try {
    const result = await api('/auth/email-code/', { method: 'POST', body: JSON.stringify({ email: profile.value.email }) })
    notice.value = result.detail
  } catch (err) { error.value = err.message } finally { sendingCode.value = false }
}

onMounted(async () => {
  try { plans.value = await api('/my-plans/') }
  catch (err) { error.value = err.message }
})

async function saveProfile() {
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    auth.user = await api('/auth/me/', { method: 'PATCH', body: JSON.stringify(profile.value) })
    profile.value = { name: auth.user.name, email: auth.user.email, email_code: '' }
    notice.value = '个人信息已保存'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function changePassword() {
  error.value = ''
  notice.value = ''
  if (password.value.new_password !== password.value.confirm_password) {
    error.value = '两次输入的新密码不一致。'
    return
  }
  busy.value = true
  try {
    const session = await api('/auth/me/', {
      method: 'PATCH',
      body: JSON.stringify({ current_password: password.value.current_password, new_password: password.value.new_password }),
    })
    auth.saveSession(session)
    password.value = { current_password: '', new_password: '', confirm_password: '' }
    notice.value = '密码已更新，当前设备已换用新登录凭证'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function removePlan(plan) {
  if (!confirm(`确认删除“${plan.title}”？\n\n该路线及相关学习进度、证据和讨论将永久删除，无法恢复。`)) return
  busy.value = true
  error.value = ''
  try {
    await api(`/my-plans/${plan.slug}/`, { method: 'DELETE' })
    plans.value = plans.value.filter((item) => item.id !== plan.id)
    notice.value = '未公开路线已删除'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="plans === null && !error" />
    <div v-else class="page-enter profile-page">
      <header class="page-heading compact"><div><span class="eyebrow">MY ACCOUNT</span><h1>个人信息</h1><p>管理对外显示的信息、登录密码和自己创建的未公开路线。</p></div></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <p v-if="notice" class="notice success">{{ notice }}</p>

      <div class="profile-grid">
        <form class="panel profile-form" @submit.prevent="saveProfile">
          <div class="section-title"><div><h2>基本资料</h2><p>用户名用于登录，创建后不能修改。</p></div></div>
          <label>用户名<input :value="auth.user?.username" disabled /></label>
          <label>显示昵称<input v-model.trim="profile.name" maxlength="80" placeholder="其他学习者看到的名字" /></label>
          <label>邮箱<input v-model.trim="profile.email" type="email" maxlength="254" autocomplete="email" placeholder="you@example.com" /></label>
          <div v-if="emailChanged" class="email-change-verification">
            <button class="button ghost" type="button" :disabled="sendingCode" @click="sendEmailCode">{{ sendingCode ? '发送中…' : '向新邮箱发送验证码' }}</button>
            <label>新邮箱验证码<input v-model.trim="profile.email_code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" required placeholder="6位验证码" /></label>
          </div>
          <button class="button primary" :disabled="busy">保存个人信息</button>
        </form>

        <form class="panel profile-form" @submit.prevent="changePassword">
          <div class="section-title"><div><h2>修改密码</h2><p>修改成功后，当前浏览器会自动换用新凭证。</p></div></div>
          <label>当前密码<input v-model="password.current_password" type="password" autocomplete="current-password" required /></label>
          <label>新密码<input v-model="password.new_password" type="password" autocomplete="new-password" minlength="8" required /></label>
          <label>确认新密码<input v-model="password.confirm_password" type="password" autocomplete="new-password" minlength="8" required /></label>
          <button class="button secondary" :disabled="busy">更新密码</button>
        </form>

      </div>

      <section class="owned-plans-section">
        <div class="section-title"><div><h2>我的未公开路线</h2><p>删除会同时移除这条路线产生的个人进度和关联内容。</p></div><RouterLink class="button ghost" to="/plans/new">创建路线</RouterLink></div>
        <div v-if="plans?.some((plan) => !plan.is_published)" class="owned-plan-list">
          <article v-for="plan in plans.filter((item) => !item.is_published)" :key="plan.id" class="panel owned-plan-row">
            <div><span class="eyebrow">{{ { draft: '草稿', pending: '审核中', rejected: '已退回' }[plan.review_status] }}</span><h3>{{ plan.title }}</h3><p>{{ plan.summary }}</p><small>{{ plan.total_days }} 天 · {{ plan.estimated_weeks }} 周</small></div>
            <div class="button-row"><RouterLink class="button ghost" :to="`/plans/${plan.slug}`">查看</RouterLink><button class="button danger-button" :disabled="busy" @click="removePlan(plan)">删除路线</button></div>
          </article>
        </div>
        <div v-else class="empty-state compact-empty"><div class="empty-orbit">净</div><h2>没有未公开路线</h2><p>公开路线不会出现在这里，也不能由用户自行删除。</p></div>
      </section>
    </div>
  </AppShell>
</template>
