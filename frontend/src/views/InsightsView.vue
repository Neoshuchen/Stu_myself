<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const data = ref(null)
const error = ref('')
const router = useRouter()
const busy = ref(null)
const gapLabels = { open: '待解决', verifying: '等待验证', resolved: '已解决' }

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

/** 移除展柜选择，保留原证据及其学习记录；失败时保留卡片。 */
async function unfeature(item) {
  busy.value = item.id
  try {
    await api(`/evidence/${item.id}/feature/`, { method: 'POST', body: JSON.stringify({ is_featured: false }) })
    data.value.showcase = data.value.showcase.filter(evidence => evidence.id !== item.id)
  } catch (err) { error.value = err.message } finally { busy.value = null }
}

/** 把选定作品文字放入社区编辑页草稿，附件保持私有，等待用户审核后发布。 */
function shareProject(item) {
  router.push({ path: '/community/new', state: { showcaseDraft: {
    title: item.title,
    content: `学习主题：${item.plan_title} · Day ${item.day_number}\n\n成果与证据：\n${item.content || '请补充成果说明。'}${item.url ? `\n作品链接：${item.url}` : ''}\n\n我的复盘：\n${item.reflection || '请补充过程、收获与下一步。'}`,
  } } })
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!data && !error" />
    <div v-else class="page-enter insights-page">
      <header class="page-heading compact"><div><span class="eyebrow">LEARNING INSIGHTS</span><h1>看见掌握，也看见缺口</h1><p>这里不评价你学得快不快，只整理已经验证的能力和下一步最值得解决的问题。</p></div><div class="button-row"><button class="button ghost" @click="download('json')">导出 JSON</button><button class="button primary" @click="download('markdown')">导出 Markdown</button></div></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <template v-if="data">
        <section class="insight-summary"><article><strong>{{ data.summary.plans }}</strong><span>学习路线</span></article><article><strong>{{ data.summary.completed_days }}</strong><span>完成学习日</span></article><article><strong>{{ data.summary.knowledge_learned }}</strong><span>已学知识点</span></article><article><strong>{{ data.summary.open_gaps }}</strong><span>待解决缺口</span></article></section>
        <section class="panel showcase-section">
          <div class="section-title"><div><span class="eyebrow">MY SHOWCASE</span><h2>私人成果展柜</h2></div><span>{{ data.showcase.length }} 件作品</span></div>
          <p>在每日学习页把值得保留的证据选入展柜。分享会先打开项目草稿，由你审核后发布。</p>
          <div v-if="data.showcase.length" class="showcase-grid">
            <article v-for="item in data.showcase" :key="item.id"><small>{{ item.plan_title }} · Day {{ item.day_number }}</small><h3>{{ item.title }}</h3><p class="content-body">{{ item.content }}</p>
              <a v-if="item.url" :href="item.url" target="_blank" rel="noopener noreferrer">打开作品链接 ↗</a>
              <a v-if="item.attachment_url" :href="item.attachment_url" target="_blank" rel="noopener noreferrer"><img v-if="item.attachment_is_image" :src="item.attachment_url" :alt="item.title" loading="lazy" /><span v-else>查看附件 {{ item.attachment_name }}</span></a>
              <details v-if="item.reflection"><summary>当日复盘</summary><p class="content-body">{{ item.reflection }}</p></details>
              <div class="button-row"><button class="button secondary" @click="shareProject(item)">整理为项目分享草稿</button><button class="button ghost" :disabled="busy !== null" @click="unfeature(item)">移出展柜</button></div>
            </article>
          </div><p v-else class="muted">还没有精选作品。去每日学习页，从一份真实证据开始。</p>
        </section>
        <section v-if="data.repeated_gaps.length" class="panel repeated-gaps"><div class="section-title"><div><span class="eyebrow">REPEATED GAPS</span><h2>反复出现的知识缺口</h2></div></div><div class="gap-cloud"><span v-for="gap in data.repeated_gaps" :key="gap.title" :class="{ repeated: gap.count > 1, resolved: !gap.open_count }">{{ gap.title }} <b>×{{ gap.count }}</b><small>{{ gap.open_count ? `${gap.open_count} 个待解决或验证` : '已解决' }}</small></span></div></section>
        <section class="insight-plans">
          <article v-for="plan in data.plans" :key="plan.enrollment_id" class="panel insight-plan">
            <header><div><span class="eyebrow">DAY {{ plan.current_day }} / {{ plan.total_days }}</span><h2>{{ plan.title }}</h2></div><RouterLink v-if="plan.status !== 'withdrawn'" :to="`/learn/${plan.enrollment_id}/${plan.current_day}`">继续学习 →</RouterLink><RouterLink v-else :to="`/plans/${plan.slug}`">重新加入路线 →</RouterLink></header>
            <div class="mastery-grid"><div><strong>{{ plan.completed_days }}</strong><span>完成天数</span></div><div><strong>{{ plan.knowledge_learned }}/{{ plan.knowledge_total }}</strong><span>知识点掌握</span></div><div><strong>{{ plan.average_recall ?? '—' }}{{ plan.average_recall !== null ? '%' : '' }}</strong><span>平均闭卷掌握</span></div><div><strong>{{ plan.open_gaps }}</strong><span>开放缺口</span></div></div>
            <div v-if="plan.gaps.length" class="gap-timeline"><article v-for="gap in plan.gaps" :key="gap.id" :class="gap.status"><span>Day {{ gap.day_number }}</span><div><b>{{ gap.title }}</b><p>{{ gap.detail || gap.day_title }}</p></div><i>{{ gapLabels[gap.status] || gap.status }}</i></article></div>
            <p v-else class="no-gaps">还没有记录知识缺口。遇到阻塞时，把问题缩小并留在当天学习页。</p>
          </article>
        </section>
      </template>
    </div>
  </AppShell>
</template>
