<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'
import { auth } from '../auth'
import AuthLayout from './AuthLayout.vue'

const router = useRouter()
const form = ref({ name: '', username: '', email: '', email_code: '', password: '', password_confirm: '', invite_code: '' })
const error = ref('')
const codeNotice = ref('')
const busy = ref(false)
const sendingCode = ref(false)

async function sendCode() {
  error.value = ''
  codeNotice.value = ''
  if (!form.value.email) {
    error.value = '请先填写邮箱。'
    return
  }
  sendingCode.value = true
  try {
    const result = await api('/auth/email-code/', { method: 'POST', body: JSON.stringify({ email: form.value.email, invite_code: form.value.invite_code }) })
    codeNotice.value = result.detail
  } catch (err) { error.value = err.message } finally { sendingCode.value = false }
}

async function submit() {
  error.value = ''
  if (form.value.password !== form.value.password_confirm) {
    error.value = '两次输入的密码不一致。'
    return
  }
  busy.value = true
  try {
    await auth.register(form.value)
    router.push('/plans')
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthLayout title="把想学，变成今天能完成" copy="一条清晰的路径、一份真实的证据，胜过无数次收藏。">
    <h2>从今天开始</h2><p class="muted">选择计划后，我们只把今天交给你。</p>
    <form class="form-stack" @submit.prevent="submit">
      <label>怎么称呼你<input v-model.trim="form.name" autocomplete="name" placeholder="例如：小林" /></label>
      <label>学习小队邀请码<input v-model.trim="form.invite_code" autocomplete="off" maxlength="12" placeholder="由小队创建者提供" /><small class="field-hint">站点启用邀请注册时必须填写。</small></label>
      <label>用户名<input v-model.trim="form.username" autocomplete="username" required placeholder="用于登录" /></label>
      <label>邮箱<div class="email-code-send"><input v-model.trim="form.email" type="email" autocomplete="email" required placeholder="you@example.com" /><button class="button ghost" type="button" :disabled="sendingCode" @click="sendCode">{{ sendingCode ? '发送中…' : '发送验证码' }}</button></div></label>
      <label>邮箱验证码<input v-model.trim="form.email_code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" required placeholder="6位验证码" /></label>
      <label>密码<input v-model="form.password" type="password" autocomplete="new-password" minlength="8" required placeholder="至少8位" /></label>
      <label>确认密码<input v-model="form.password_confirm" type="password" autocomplete="new-password" minlength="8" required placeholder="再次输入密码" /></label>
      <p v-if="codeNotice" class="notice success">{{ codeNotice }}</p>
      <p v-if="error" class="form-error">{{ error }}</p>
      <button class="button primary wide" :disabled="busy">{{ busy ? '正在创建…' : '创建并选择计划' }}</button>
    </form>
    <p class="form-foot">已经有账号？<RouterLink to="/login">直接登录</RouterLink></p>
    <p class="form-foot">创建账号即表示你已阅读 <RouterLink to="/privacy">隐私说明</RouterLink> 与 <RouterLink to="/community-guidelines">社区规范</RouterLink>。</p>
  </AuthLayout>
</template>
