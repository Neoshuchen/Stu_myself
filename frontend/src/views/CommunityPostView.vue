<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const comment = ref('')
const replyTo = ref(null)
const error = ref('')
const busy = ref(false)
const types = { share: '技术分享', question: '问题求助', check_in: '学习打卡', project: '项目展示' }

onMounted(load)
async function load() {
  try { post.value = await api(`/community/posts/${route.params.id}/`) } catch (err) { error.value = err.message }
}
async function like() {
  if (!auth.loggedIn) return router.push({ path: '/login', query: { next: route.fullPath } })
  const data = await api(`/community/posts/${post.value.id}/like/`, { method: 'POST' })
  post.value.liked = data.liked
  post.value.like_count = data.like_count
}
async function addComment() {
  busy.value = true
  try {
    await api(`/community/posts/${post.value.id}/comments/`, { method: 'POST', body: JSON.stringify({ content: comment.value, parent: replyTo.value?.id || null }) })
    comment.value = ''
    replyTo.value = null
    await load()
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
async function remove(kind, id) {
  if (!confirm('确认删除这条内容？')) return
  await api(`/community/${kind}/${id}/`, { method: 'DELETE' })
  if (kind === 'posts') router.push(post.value.plan_slug ? `/plans/${post.value.plan_slug}/community` : '/community')
  else await load()
}
async function solve() {
  const data = await api(`/community/posts/${post.value.id}/solve/`, { method: 'POST' })
  post.value.is_solved = data.is_solved
}
async function report(kind, id) {
  if (!auth.loggedIn) return router.push({ path: '/login', query: { next: route.fullPath } })
  const reason = prompt('请简要说明举报原因')?.trim()
  if (!reason) return
  try { await api('/community/reports/', { method: 'POST', body: JSON.stringify({ [kind]: id, reason }) }); alert('举报已提交，管理员会进行处理。') }
  catch (err) { error.value = err.message }
}
async function suggestCourseUpdate() {
  const title = prompt('课程补充标题', post.value.title)?.trim()
  if (!title) return
  try {
    await api('/course-suggestions/', { method: 'POST', body: JSON.stringify({ post: post.value.id, plan_day: post.value.plan_day, title, content: post.value.content }) })
    alert('已提交课程补充建议，管理员审核采纳后会显示在对应学习日。')
  } catch (err) { error.value = err.message }
}
function dateText(value) { return new Intl.DateTimeFormat('zh-CN', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value)) }
</script>

<template>
  <AppShell>
    <LoadingState v-if="!post && !error" />
    <p v-else-if="error && !post" class="notice error">{{ error }}</p>
    <div v-else class="page-enter post-page">
      <nav class="post-breadcrumb"><RouterLink :to="post.plan_slug ? `/plans/${post.plan_slug}/community` : '/community'">← {{ post.plan_title || '学习社区' }}</RouterLink><span v-if="post.day_number">Day {{ post.day_number }}</span></nav>
      <article class="panel post-detail">
        <header><div class="post-meta"><span :class="['post-type', post.post_type]">{{ types[post.post_type] }}</span><span v-if="post.is_solved" class="solved-badge">已解决</span><span>{{ dateText(post.created_at) }}</span></div><h1>{{ post.title }}</h1><div class="post-author"><span class="community-avatar">{{ post.author.name.slice(0, 1) }}</span><div><b>{{ post.author.name }}</b><small>@{{ post.author.username }}</small></div></div></header>
        <div class="post-content">{{ post.content }}</div>
        <div v-if="post.images?.length" :class="['post-gallery', `count-${post.images.length}`]">
          <a v-for="image in post.images" :key="image.id" :href="image.url" target="_blank" rel="noopener"><img :src="image.url" :alt="image.alt_text || `${post.title}配图`" :width="image.width" :height="image.height" loading="lazy" /></a>
        </div>
        <footer><button :class="['like-button', { active: post.liked }]" @click="like">{{ post.liked ? '♥' : '♡' }} {{ post.like_count }}</button><button v-if="post.post_type === 'question' && (post.owned || auth.user?.is_staff)" class="text-action" @click="solve">{{ post.is_solved ? '重新打开问题' : '标记已解决' }}</button><button v-if="post.owned && post.plan_day" class="text-action" @click="suggestCourseUpdate">推荐为课程补充</button><span></span><RouterLink v-if="post.owned" class="text-action" :to="`/community/posts/${post.id}/edit`">编辑</RouterLink><button v-if="post.owned || auth.user?.is_staff" class="text-action danger-text" @click="remove('posts', post.id)">删除</button><button v-else class="text-action" @click="report('post', post.id)">举报</button></footer>
      </article>
      <section class="comments-section">
        <div class="section-title"><h2>{{ post.comment_count }} 条讨论</h2></div>
        <form v-if="auth.loggedIn" class="panel comment-form" @submit.prevent="addComment"><p v-if="replyTo">正在回复 <b>{{ replyTo.author.name }}</b><button type="button" @click="replyTo = null">取消</button></p><textarea v-model.trim="comment" required rows="4" placeholder="补充一个具体观点、验证结果或解决思路……"></textarea><button class="button secondary" :disabled="busy">参与讨论</button></form>
        <RouterLink v-else class="panel login-to-comment" :to="`/login?next=${route.fullPath}`">登录后参与讨论 →</RouterLink>
        <article v-for="item in post.comments" :key="item.id" class="comment-card panel"><div class="community-avatar">{{ item.author.name.slice(0, 1) }}</div><div><header><b>{{ item.author.name }}</b><span>{{ dateText(item.created_at) }}</span><small v-if="item.parent">回复 #{{ item.parent }}</small></header><p>{{ item.content }}</p><footer><button v-if="auth.loggedIn" @click="replyTo = item">回复</button><button v-if="item.owned || auth.user?.is_staff" @click="remove('comments', item.id)">删除</button><button v-else-if="auth.loggedIn" @click="report('comment', item.id)">举报</button></footer></div></article>
      </section>
    </div>
  </AppShell>
</template>
