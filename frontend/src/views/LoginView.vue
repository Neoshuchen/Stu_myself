<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { auth } from '../auth'
import AuthLayout from './AuthLayout.vue'

const route = useRoute()
const router = useRouter()
const form = ref({ username: '', password: '' })
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  try {
    await auth.login(form.value)
    router.push(route.query.next || '/dashboard')
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AuthLayout title="继续你的学习节奏" copy="今天不必完成很多，只需要完成真正重要的一件事。">
    <h2>欢迎回来</h2><p class="muted">继续上次停下的地方。</p>
    <form class="form-stack" @submit.prevent="submit">
      <label>用户名<input v-model.trim="form.username" autocomplete="username" required placeholder="你的用户名" /></label>
      <label>密码<input v-model="form.password" type="password" autocomplete="current-password" required placeholder="至少8位" /></label>
      <p v-if="error" class="form-error">{{ error }}</p>
      <button class="button primary wide" :disabled="busy">{{ busy ? '正在进入…' : '进入今日学习' }}</button>
    </form>
    <p class="form-foot">还没有账号？<RouterLink to="/register">创建一个</RouterLink></p>
    <p class="form-foot"><RouterLink to="/privacy">隐私说明</RouterLink> · <RouterLink to="/community-guidelines">社区规范</RouterLink></p>
  </AuthLayout>
</template>
