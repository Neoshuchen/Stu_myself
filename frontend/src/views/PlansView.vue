<script setup>
import { onMounted, ref } from 'vue'

import { api } from '../api'
import { auth } from '../auth'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const plans = ref(null)
const error = ref('')
onMounted(async () => {
  try { plans.value = await api('/plans/') } catch (err) { error.value = err.message }
})
</script>

<template>
  <AppShell>
    <LoadingState v-if="!plans && !error" />
    <div v-else class="page-enter">
      <header class="page-heading compact"><div><h1>选择一条值得走完的路</h1><p>从公开计划开始，或者把自己的目标拆成每天可以完成的任务。</p></div><RouterLink v-if="auth.loggedIn" class="button primary" to="/plans/new">创建我的路线</RouterLink></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <section v-else class="plans-grid">
        <RouterLink v-for="plan in plans" :key="plan.id" :to="`/plans/${plan.slug}`" class="plan-card" :style="{ '--accent-a': plan.accent_start, '--accent-b': plan.accent_end }">
          <div class="plan-cover">
            <div class="plan-card-meta"><span>{{ plan.estimated_weeks }} 周 / {{ plan.total_days }} 天</span><span v-if="plan.owned" :class="['review-badge', plan.review_status]">{{ { draft: '草稿', pending: '审核中', approved: '已发布', rejected: '已退回' }[plan.review_status] }}</span></div>
          </div>
          <div class="plan-body">
            <h2>{{ plan.title }}</h2><p>{{ plan.summary }}</p>
            <div class="plan-foot"><span>{{ plan.owned ? '我的路线' : `由 ${plan.creator_name} 创建` }}</span><b>{{ plan.owned && plan.review_status !== 'approved' ? '查看与管理' : '查看计划' }}</b></div>
          </div>
        </RouterLink>
        <article class="plan-card coming-soon"><div><h2>更多计划正在整理</h2><p>先把一条路径做深、做实，再让选择变多。</p></div></article>
      </section>
    </div>
  </AppShell>
</template>
