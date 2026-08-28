<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const route = useRoute()
const posts = ref(null)
const plan = ref(null)
const error = ref('')
const type = ref('')
const sort = ref('latest')
const types = { share: '技术分享', question: '问题求助', check_in: '学习打卡', project: '项目展示' }
const isGroup = computed(() => Boolean(route.params.slug))
const newPostLink = computed(() => isGroup.value ? `/plans/${route.params.slug}/community/new` : '/community/new')

onMounted(load)
watch([type, sort], load)

async function load() {
  posts.value = null
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (isGroup.value) params.set('plan', route.params.slug)
    else params.set('scope', 'global')
    if (type.value) params.set('type', type.value)
    if (sort.value === 'hot') params.set('sort', 'hot')
    if (sort.value === 'unsolved') params.set('solved', 'false')
    const requests = [api(`/community/posts/?${params}`)]
    if (isGroup.value) requests.push(api(`/plans/${route.params.slug}/`))
    const [items, planDetail] = await Promise.all(requests)
    posts.value = items
    plan.value = planDetail || null
  } catch (err) { error.value = err.message }
}

function dateText(value) {
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!posts && !error" />
    <div v-else class="page-enter community-page">
      <header class="community-hero">
        <div><span class="eyebrow">{{ isGroup ? 'LEARNING GROUP' : 'LEARNING COMMONS' }}</span><h1>{{ isGroup ? `${plan?.title || ''} · 学习小组` : '把学到的，讲给同行的人' }}</h1><p>{{ isGroup ? '这里的讨论只属于已经加入这条路线的学习者。分享进度，也把具体问题留下来。' : '分享技术、提出好问题、展示真实作品。让每一次表达都成为学习证据。' }}</p></div>
        <RouterLink v-if="auth.loggedIn" class="button light" :to="newPostLink">写一篇</RouterLink>
        <RouterLink v-else class="button light" to="/login?next=/community/new">登录后分享</RouterLink>
      </header>

      <div class="community-toolbar">
        <div class="filter-chips"><button :class="{ active: !type }" @click="type = ''">全部</button><button v-for="(label, key) in types" :key="key" :class="{ active: type === key }" @click="type = key">{{ label }}</button></div>
        <select v-model="sort" aria-label="帖子排序"><option value="latest">最新发布</option><option value="hot">热门讨论</option><option value="unsolved">待解决问题</option></select>
      </div>
      <p v-if="error" class="notice error">{{ error }}</p>
      <section v-else-if="posts.length" class="community-feed">
        <RouterLink v-for="post in posts" :key="post.id" :to="`/community/posts/${post.id}`" class="community-card">
          <div class="community-avatar">{{ post.author.name.slice(0, 1).toUpperCase() }}</div>
          <article>
            <div class="post-meta"><span :class="['post-type', post.post_type]">{{ types[post.post_type] }}</span><span v-if="post.is_solved" class="solved-badge">已解决</span><span>{{ post.author.name }}</span><span>{{ dateText(post.created_at) }}</span><span v-if="post.day_number">Day {{ post.day_number }}</span></div>
            <h2>{{ post.title }}</h2><p>{{ post.content }}</p>
            <img v-if="post.images?.length" class="community-card-image" :src="post.images[0].url" :alt="post.images[0].alt_text || `${post.title}配图`" :width="post.images[0].width" :height="post.images[0].height" loading="lazy" />
            <footer><span>♡ {{ post.like_count }}</span><span>评论 {{ post.comment_count }}</span><span v-if="post.plan_title">{{ post.plan_title }}</span></footer>
          </article>
        </RouterLink>
      </section>
      <section v-else class="empty-state"><div class="empty-orbit">言</div><h2>这里还很安静</h2><p>分享一个具体收获，或提出一个已经缩小范围的问题。</p><RouterLink v-if="auth.loggedIn" class="button primary" :to="newPostLink">成为第一个分享者</RouterLink></section>
    </div>
  </AppShell>
</template>
