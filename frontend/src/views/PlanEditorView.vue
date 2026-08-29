<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const DIAGNOSIS_LABELS = {
  topics: '文档知识主题',
  gaps: '仍有缺口',
  assumptions: '生成假设',
  warnings: '需要注意',
}

const route = useRoute()
const router = useRouter()
const loading = ref(Boolean(route.params.slug))
const error = ref('')
const importError = ref('')
const importNotice = ref('')
const importing = ref(false)
const saveAction = ref('draft')
const savingAction = ref('')
const credentials = ref([])
const roadmapFiles = ref([])
const roadmapPreview = ref(null)
const routeInfoSection = ref(null)
const generation = ref({
  credential: '',
  target_days: 14,
  daily_minutes: 60,
  learner_background: '',
  goal: '',
  allow_supplement: false,
})
const form = ref({ title: '', subtitle: '', summary: '', audience: '', days: [] })
const editing = computed(() => Boolean(route.params.slug))
const busy = computed(() => Boolean(savingAction.value))
const hasCredentials = computed(() => credentials.value.length > 0)
const canGenerate = computed(() => (
  roadmapFiles.value.length > 0
  && Boolean(generation.value.credential)
  && !importing.value
))
const roadmapSourceSummary = computed(() => {
  if (!roadmapPreview.value) return ''
  const sources = roadmapPreview.value.sources?.length
    ? roadmapPreview.value.sources
    : [roadmapPreview.value.source].filter(Boolean)
  return `${sources.map((item) => item.filename).join('、')} · ${roadmapPreview.value.source.characters} 字符`
})

function blankDay(number) {
  const week = Math.ceil(number / 7)
  return { day_number: number, phase: '自主学习', week_number: week, week_title: `第 ${week} 周`, title: '', core_knowledge: '', hands_on_task: '', acceptance_text: '', estimated_minutes: 60 }
}

function addDay() { form.value.days.push(blankDay(form.value.days.length + 1)) }

function removeDay(index) {
  if (form.value.days.length === 1) return
  form.value.days.splice(index, 1)
  form.value.days.forEach((day, i) => {
    day.day_number = i + 1
    day.week_number = Math.ceil((i + 1) / 7)
    if (!day.week_title.trim() || /^第 \d+ 周$/.test(day.week_title)) day.week_title = `第 ${day.week_number} 周`
  })
}

function routeHasContent() {
  return Boolean(
    form.value.title.trim()
    || form.value.subtitle.trim()
    || form.value.summary.trim()
    || form.value.audience.trim()
    || form.value.days.some((day) => day.title.trim() || day.core_knowledge.trim() || day.hands_on_task.trim() || day.acceptance_text.trim()),
  )
}

async function loadCredentials(preferredId = null) {
  if (editing.value) return
  try {
    credentials.value = await api('/ai/credentials/')
    const preferred = credentials.value.find((item) => item.id === preferredId)
    const selected = credentials.value.find((item) => item.id === Number(generation.value.credential))
    generation.value.credential = preferred?.id || selected?.id || credentials.value[0]?.id || ''
    importError.value = ''
  } catch (err) {
    credentials.value = []
    generation.value.credential = ''
    importError.value = err.message
  }
}

function credentialsChanged(event) {
  loadCredentials(event.detail?.id || null)
}

function openAiConfiguration() {
  window.dispatchEvent(new Event('open-ai-configuration'))
}

function roadmapFileChanged(event) {
  roadmapFiles.value = Array.from(event.target.files || [])
  importError.value = ''
  if (!roadmapFiles.value.length) {
    importNotice.value = ''
  } else if (roadmapFiles.value.length === 1) {
    importNotice.value = `已选择 ${roadmapFiles.value[0].name}`
  } else {
    importNotice.value = `已选择 ${roadmapFiles.value.length} 个 Markdown 文件：${roadmapFiles.value.map((file) => file.name).join('、')}`
  }
}

function applyDraft(draft) {
  form.value = {
    title: draft.title || '',
    subtitle: draft.subtitle || '',
    summary: draft.summary || '',
    audience: draft.audience || '',
    days: (draft.days || []).map((day) => ({
      ...day,
      acceptance_text: (day.acceptance_criteria || []).join('\n'),
    })),
  }
}

async function generateRoadmap() {
  importError.value = ''
  importNotice.value = ''
  if (!canGenerate.value) {
    importError.value = '请至少选择一个 Markdown 文件和模型配置。'
    return
  }
  if (routeHasContent() && !confirm('生成结果会替换当前尚未保存的路线内容，确认继续吗？')) return

  const body = new FormData()
  roadmapFiles.value.forEach((file) => body.append('files', file))
  body.append('credential', generation.value.credential)
  body.append('target_days', generation.value.target_days)
  body.append('daily_minutes', generation.value.daily_minutes)
  body.append('learner_background', generation.value.learner_background)
  body.append('goal', generation.value.goal)
  body.append('allow_supplement', String(generation.value.allow_supplement))
  importing.value = true
  try {
    roadmapPreview.value = await api('/my-plans/markdown-preview/', { method: 'POST', body })
    applyDraft(roadmapPreview.value.draft)
    importNotice.value = '路线草稿已生成并回填，但尚未保存。请先诊断和修改，再决定如何采用。'
    await nextTick()
    routeInfoSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (err) {
    importError.value = err.message
  } finally {
    importing.value = false
  }
}

function discardPreview() {
  if (!confirm('确认放弃本次生成结果和已经做出的修改吗？')) return
  roadmapPreview.value = null
  form.value = { title: '', subtitle: '', summary: '', audience: '', days: [blankDay(1)] }
  importNotice.value = '已放弃生成结果，可以重新生成或手工创建路线。'
}

function planPayload() {
  return {
    title: form.value.title,
    subtitle: form.value.subtitle,
    summary: form.value.summary,
    audience: form.value.audience,
    days: form.value.days.map(({ acceptance_text, ...day }) => ({
      ...day,
      acceptance_criteria: acceptance_text.split('\n').map((item) => item.trim()).filter(Boolean),
    })),
  }
}

async function save() {
  const action = saveAction.value
  error.value = ''
  savingAction.value = action
  let created = null
  try {
    const plan = await api(editing.value ? `/my-plans/${route.params.slug}/` : '/my-plans/', {
      method: editing.value ? 'PUT' : 'POST',
      body: JSON.stringify(planPayload()),
    })
    created = plan
    if (editing.value || action === 'draft') {
      await router.push(`/plans/${plan.slug}`)
      return
    }
    if (action === 'enroll') {
      const enrollment = await api(`/my-plans/${plan.slug}/enroll/`, { method: 'POST' })
      await router.push(`/learn/${enrollment.id}/1`)
      return
    }
    await api(`/my-plans/${plan.slug}/submit/`, { method: 'POST' })
    await router.push(`/plans/${plan.slug}`)
  } catch (err) {
    if (created) {
      await router.replace(`/plans/${created.slug}/edit`)
      error.value = `路线已保存为私有草稿，但后续操作失败：${err.message}`
    } else {
      error.value = err.message
    }
  } finally {
    savingAction.value = ''
    saveAction.value = 'draft'
  }
}

onMounted(async () => {
  window.addEventListener('ai-credentials-changed', credentialsChanged)
  if (!editing.value) {
    addDay()
    await loadCredentials()
    return
  }
  try {
    const plan = await api(`/my-plans/${route.params.slug}/`)
    form.value = { ...plan, days: plan.days.map((day) => ({ ...day, acceptance_text: day.acceptance_criteria.join('\n') })) }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => window.removeEventListener('ai-credentials-changed', credentialsChanged))
</script>

<template>
  <AppShell>
    <LoadingState v-if="loading" />
    <div v-else class="page-enter plan-editor">
      <header class="page-heading compact"><div><h1>{{ editing ? '编辑学习路线' : '创建自己的学习路线' }}</h1><p>先定义结果，再把它拆成每天可完成、可验收的任务。</p></div></header>
      <p v-if="error" class="notice error" role="alert">{{ error }}</p>

      <form class="editor-form" @submit.prevent="save">
        <details v-if="!editing" class="editor-section roadmap-generator" open>
          <summary><span><b>AI 从 Markdown 生成</b><small>让你选择的模型梳理资料，结果先预览、修改，再决定是否采用。</small></span><i>生成设置</i></summary>
          <div class="roadmap-generator-body">
            <div class="editor-fields roadmap-generator-fields">
              <label class="full">Markdown 学习资料<input type="file" accept=".md,text/markdown,text/plain" multiple @change="roadmapFileChanged" /><small>可同时选择多个完整的 .md 文件；数量遵循站点附件上限，任一文件超限都不会静默截断。</small></label>
              <label>模型配置<select v-model="generation.credential" required><option disabled value="">请选择账号配置</option><option v-for="item in credentials" :key="item.id" :value="item.id">{{ item.name }} · {{ item.model }} · ····{{ item.key_last_four }}</option></select></label>
              <div class="roadmap-config-action"><button class="button ghost" type="button" @click="openAiConfiguration">＋ 新增模型配置</button><small v-if="!hasCredentials">还没有长期配置，请先新增并保存。</small></div>
              <label>目标天数<input v-model.number="generation.target_days" type="number" min="1" max="30" required /></label>
              <label>每日时间（分钟）<input v-model.number="generation.daily_minutes" type="number" min="15" max="240" required /></label>
              <label class="full">当前基础<textarea v-model.trim="generation.learner_background" rows="2" maxlength="500" placeholder="可选，例如：掌握 Python 语法，还没有 Django 项目经验"></textarea></label>
              <label class="full">最终目标<textarea v-model.trim="generation.goal" rows="2" maxlength="500" placeholder="可选，例如：独立完成一个带权限和测试的 Django API"></textarea></label>
              <label class="full roadmap-checkbox"><input v-model="generation.allow_supplement" type="checkbox" /><span>允许模型补充文档没有覆盖、但路线必须具备的基础知识；补充假设会单独展示。</span></label>
            </div>
            <div class="roadmap-generate-actions">
              <p>全部 Markdown 会在一次请求中发送给所选第三方模型。不要上传密码、Token、隐私资料或无权处理的内容。</p>
              <button class="button primary" type="button" :disabled="!canGenerate" @click="generateRoadmap">{{ importing ? '正在梳理资料…' : '生成学习路线草稿' }}</button>
            </div>
            <p v-if="importError" class="notice error" role="alert">{{ importError }}</p>
            <p v-if="importNotice" class="notice success" aria-live="polite">{{ importNotice }}</p>
          </div>
        </details>

        <section v-if="roadmapPreview" class="editor-section roadmap-diagnosis">
          <div class="editor-section-heading"><span>生成诊断</span><p>{{ roadmapSourceSummary }} · {{ roadmapPreview.provider.name }} / {{ roadmapPreview.provider.model }}<template v-if="roadmapPreview.usage"> · 输入 {{ roadmapPreview.usage.input_tokens }} / 输出 {{ roadmapPreview.usage.output_tokens }} tokens</template></p></div>
          <div class="roadmap-diagnosis-grid">
            <article v-for="(label, key) in DIAGNOSIS_LABELS" :key="key"><h3>{{ label }}</h3><ul v-if="roadmapPreview.diagnosis[key].length"><li v-for="item in roadmapPreview.diagnosis[key]" :key="item">{{ item }}</li></ul><p v-else>模型未报告此项。</p></article>
          </div>
          <div class="roadmap-diagnosis-actions"><span>以下路线尚未保存，你可以继续逐项修改。</span><button class="button ghost" type="button" @click="discardPreview">放弃此次结果</button></div>
        </section>

        <section ref="routeInfoSection" class="editor-section">
          <div class="editor-section-heading"><span>路线信息</span><p>让其他学习者一眼看懂要学什么，以及学完能做到什么。</p></div>
          <div class="editor-fields">
            <label>路线名称<input v-model.trim="form.title" required maxlength="160" placeholder="例如：30天掌握 Python 自动化" /></label>
            <label>一句话目标<input v-model.trim="form.subtitle" maxlength="200" placeholder="完成后能够独立做什么" /></label>
            <label class="full">路线介绍<textarea v-model.trim="form.summary" required rows="4" placeholder="说明学习目标、主要内容和最终成果"></textarea></label>
            <label class="full">适合人群<input v-model.trim="form.audience" maxlength="240" placeholder="例如：有 Python 基础，希望进入数据采集方向的学习者" /></label>
          </div>
        </section>

        <section class="editor-section">
          <div class="editor-section-heading"><span>每日安排</span><p>每一天都需要知识点、动手任务和至少一个验收标准。</p></div>
          <div class="editor-days">
            <article v-for="(day, index) in form.days" :key="day.day_number" class="editor-day">
              <header><strong>Day {{ day.day_number }}</strong><button type="button" :disabled="form.days.length === 1" @click="removeDay(index)">删除</button></header>
              <div class="editor-fields day-fields">
                <label>阶段<input v-model.trim="day.phase" required /></label><label>周标题<input v-model.trim="day.week_title" required /></label>
                <label class="full">当天主题<input v-model.trim="day.title" required placeholder="今天要完成什么主题" /></label>
                <label class="full">核心知识点<textarea v-model.trim="day.core_knowledge" required rows="3" placeholder="使用逗号分隔，例如：请求、响应、状态码、会话"></textarea></label>
                <label class="full">动手任务<textarea v-model.trim="day.hands_on_task" required rows="3" placeholder="描述一个可以独立复现的具体任务"></textarea></label>
                <label class="full">验收标准<textarea v-model="day.acceptance_text" required rows="3" placeholder="每行一个验收标准"></textarea></label>
                <label>预计时长（分钟）<input v-model.number="day.estimated_minutes" type="number" min="15" max="1440" required /></label>
              </div>
            </article>
          </div>
          <button class="button add-day" type="button" @click="addDay">添加一天</button>
        </section>

        <footer class="editor-actions">
          <span v-if="roadmapPreview">模型结果只是草稿。保存后可以自己学习，也可以提交管理员审核后公开。</span>
          <span v-else>保存后可以先加入自己的路径，也可以提交管理员审核后公开。</span>
          <div v-if="roadmapPreview && !editing" class="button-row">
            <button class="button ghost" :disabled="busy" @click="saveAction = 'draft'">{{ savingAction === 'draft' ? '正在保存' : '仅保存草稿' }}</button>
            <button class="button secondary" :disabled="busy" @click="saveAction = 'enroll'">{{ savingAction === 'enroll' ? '正在加入' : '加入我的学习规划' }}</button>
            <button class="button primary" :disabled="busy" @click="saveAction = 'submit'">{{ savingAction === 'submit' ? '正在提交' : '提交公开审核' }}</button>
          </div>
          <button v-else class="button primary" :disabled="busy" @click="saveAction = 'draft'">{{ busy ? '正在保存' : editing ? '保存修改' : '保存学习路线' }}</button>
        </footer>
      </form>
    </div>
  </AppShell>
</template>
