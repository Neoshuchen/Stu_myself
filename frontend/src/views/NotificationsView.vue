<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const router = useRouter()
const data = ref(null)
const error = ref('')
const busy = ref(false)

onMounted(load)

async function load() {
  error.value = ''
  try { data.value = await api('/notifications/') } catch (err) { error.value = err.message }
}

async function openNotification(item) {
  if (!item.read) await api(`/notifications/${item.id}/read/`, { method: 'POST' })
  window.dispatchEvent(new Event('notifications-changed'))
  if (item.url) router.push(item.url)
  else load()
}

async function readAll() {
  busy.value = true
  try {
    await api('/notifications/read-all/', { method: 'POST' })
    await load()
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

function formatTime(value) {
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!data && !error" />
    <div v-else class="notification-page page-enter">
      <header class="page-heading compact"><div><span class="eyebrow">NOTIFICATIONS</span><h1>需要你回应的学习动态</h1><p>只保留会影响学习和朋友协作的消息。</p></div><button v-if="data?.unread_count" class="button ghost" :disabled="busy" @click="readAll">全部已读</button></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <RouterLink v-if="data?.due_review_count" class="review-notice panel" to="/review"><div><span class="eyebrow">RECALL DUE</span><h2>{{ data.due_review_count }} 项复习已经到期</h2><p>先花 3 分钟回忆，再继续今天的课程。</p></div><strong>去复习 →</strong></RouterLink>
      <section v-if="data?.items.length" class="notification-list">
        <button v-for="item in data.items" :key="item.id" :class="['panel', { unread: !item.read }]" @click="openNotification(item)">
          <i></i><div><span>{{ item.kind }} · {{ formatTime(item.created_at) }}</span><h2>{{ item.title }}</h2><p>{{ item.body }}</p></div><strong>查看 →</strong>
        </button>
      </section>
      <section v-else-if="data" class="panel empty-notifications"><h2>现在没有新通知</h2><p>朋友回复、互评结果、答疑和知识缺口验证会出现在这里。</p></section>
    </div>
  </AppShell>
</template>
