<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import EmptyState from '../components/EmptyState.vue'
import LoadingState from '../components/LoadingState.vue'

const plans = ref(null)
const error = ref('')
const route = useRoute()
const router = useRouter()
const search = computed({
  get: () => typeof route.query.q === 'string' ? route.query.q : '',
  set: value => router.replace({ query: { ...route.query, q: value || undefined } }),
})
const filteredPlans = computed(() => {
  const query = search.value.trim().toLocaleLowerCase()
  return (plans.value || []).filter(plan => [plan.title, plan.summary, plan.audience].join(' ').toLocaleLowerCase().includes(query))
})
onBeforeRouteLeave(() => {
  window.history.replaceState({ ...window.history.state, plansScroll: window.scrollY }, '')
})
onMounted(async () => {
  const scrollTop = window.history.state?.plansScroll || 0
  try {
    plans.value = await api('/plans/')
    // 列表高度依赖接口结果，必须等卡片渲染后恢复本历史条目的滚动位置。
    await nextTick()
    window.scrollTo({ top: scrollTop, behavior: 'instant' })
  } catch (err) { error.value = err.message }
})
</script>

<template>
  <AppShell>
    <LoadingState v-if="!plans && !error" />
    <div v-else class="page-enter">
      <header class="page-heading compact"><div><span class="eyebrow">学习路线</span><h1>选择一条值得走完的路</h1><p>找到方向，把想学的事变成每天可完成的一步。</p></div><RouterLink v-if="auth.loggedIn" class="button primary" to="/plans/new">＋ 创建我的路线</RouterLink></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <template v-else>
        <div class="plans-toolbar">
          <label class="plan-search"><span>搜索路线</span><input v-model="search" type="search" aria-label="搜索路线" placeholder="输入主题、技能或学习目标" /></label>
          <span role="status">{{ filteredPlans.length }} 条路线</span>
        </div>
        <section v-if="filteredPlans.length" class="plans-grid" aria-label="学习路线列表">
          <RouterLink v-for="plan in filteredPlans" :key="plan.id" :to="`/plans/${plan.slug}`" class="plan-card" :style="{ '--accent-a': plan.accent_start }">
            <div class="plan-body">
              <div class="plan-card-meta"><span class="plan-symbol" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v15M3 4c3-1 6-1 9 1 3-2 6-2 9-1v15c-3-1-6-1-9 1-3-2-6-2-9-1z"/></svg></span><span>{{ plan.estimated_weeks }} 周 · {{ plan.total_days }} 天</span><span v-if="plan.owned" :class="['review-badge', plan.review_status]">{{ { draft: '草稿', pending: '审核中', approved: '已发布', rejected: '已退回' }[plan.review_status] }}</span><span v-else-if="plan.enrolled" class="review-badge approved">已加入</span></div>
              <h2>{{ plan.title }}</h2><p>{{ plan.summary }}</p>
              <p v-if="plan.audience" class="plan-audience"><b>适合谁</b>{{ plan.audience }}</p>
              <div class="plan-foot"><span>{{ plan.owned ? '我的路线' : `由 ${plan.creator_name} 创建` }}</span><b>{{ plan.owned && plan.review_status !== 'approved' ? '查看与管理' : '查看路线' }} <span aria-hidden="true">↗</span></b></div>
            </div>
          </RouterLink>
        </section>
        <EmptyState v-else :title="search.trim() ? '没有找到匹配的路线' : '你的下一段学习，从这里开始'" :copy="search.trim() ? '换一个关键词，或清除搜索看看全部路线。' : '暂时没有可浏览的路线，你可以创建自己的学习路线。'" :action="search.trim() ? '清除搜索' : undefined" @action="search = ''" />
      </template>
    </div>
  </AppShell>
</template>
