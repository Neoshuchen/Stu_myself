<script setup>
import { onMounted, ref } from 'vue'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const data = ref(null)
const error = ref('')

onMounted(async () => {
  try { data.value = await api('/insights/') } catch (err) { error.value = err.message }
})

async function download(format) {
  try {
    const file = await api(`/insights/export/?type=${format}`)
    const blob = new Blob([file.content], { type: file.mime })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = file.filename
    link.click()
    URL.revokeObjectURL(link.href)
  } catch (err) { error.value = err.message }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!data && !error" />
    <div v-else class="page-enter insights-page">
      <header class="page-heading compact"><div><span class="eyebrow">LEARNING INSIGHTS</span><h1>看见掌握，也看见缺口</h1><p>这里不评价你学得快不快，只整理已经验证的能力和下一步最值得解决的问题。</p></div><div class="button-row"><button class="button ghost" @click="download('json')">导出 JSON</button><button class="button primary" @click="download('markdown')">导出 Markdown</button></div></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <template v-else>
        <section class="insight-summary"><article><strong>{{ data.summary.plans }}</strong><span>学习路线</span></article><article><strong>{{ data.summary.completed_days }}</strong><span>完成学习日</span></article><article><strong>{{ data.summary.knowledge_learned }}</strong><span>已学知识点</span></article><article><strong>{{ data.summary.open_gaps }}</strong><span>待解决缺口</span></article></section>
        <section v-if="data.repeated_gaps.length" class="panel repeated-gaps"><div class="section-title"><div><span class="eyebrow">REPEATED GAPS</span><h2>反复出现的知识缺口</h2></div></div><div class="gap-cloud"><span v-for="gap in data.repeated_gaps" :key="gap.title" :class="{ repeated: gap.count > 1, resolved: !gap.open_count }">{{ gap.title }} <b>×{{ gap.count }}</b><small>{{ gap.open_count ? `${gap.open_count} 个待解决` : '已解决' }}</small></span></div></section>
        <section class="insight-plans">
          <article v-for="plan in data.plans" :key="plan.enrollment_id" class="panel insight-plan">
            <header><div><span class="eyebrow">DAY {{ plan.current_day }} / {{ plan.total_days }}</span><h2>{{ plan.title }}</h2></div><RouterLink :to="`/learn/${plan.enrollment_id}/${plan.current_day}`">继续学习 →</RouterLink></header>
            <div class="mastery-grid"><div><strong>{{ plan.completed_days }}</strong><span>完成天数</span></div><div><strong>{{ plan.knowledge_learned }}/{{ plan.knowledge_total }}</strong><span>知识点掌握</span></div><div><strong>{{ plan.average_recall ?? '—' }}{{ plan.average_recall !== null ? '%' : '' }}</strong><span>平均闭卷掌握</span></div><div><strong>{{ plan.open_gaps }}</strong><span>开放缺口</span></div></div>
            <div v-if="plan.gaps.length" class="gap-timeline"><article v-for="gap in plan.gaps" :key="gap.id" :class="gap.status"><span>Day {{ gap.day_number }}</span><div><b>{{ gap.title }}</b><p>{{ gap.detail || gap.day_title }}</p></div><i>{{ gap.status === 'open' ? '待解决' : '已解决' }}</i></article></div>
            <p v-else class="no-gaps">还没有记录知识缺口。遇到阻塞时，把问题缩小并留在当天学习页。</p>
          </article>
        </section>
      </template>
    </div>
  </AppShell>
</template>
