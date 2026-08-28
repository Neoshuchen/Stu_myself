<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const route = useRoute()
const router = useRouter()
const busy = ref(false)
const loading = ref(Boolean(route.params.slug))
const error = ref('')
const form = ref({ title: '', subtitle: '', summary: '', audience: '', days: [] })
const editing = computed(() => Boolean(route.params.slug))

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

onMounted(async () => {
  if (!editing.value) { addDay(); return }
  try {
    const plan = await api(`/my-plans/${route.params.slug}/`)
    form.value = { ...plan, days: plan.days.map(day => ({ ...day, acceptance_text: day.acceptance_criteria.join('\n') })) }
  } catch (err) { error.value = err.message } finally { loading.value = false }
})

async function save() {
  error.value = ''
  busy.value = true
  const payload = {
    title: form.value.title,
    subtitle: form.value.subtitle,
    summary: form.value.summary,
    audience: form.value.audience,
    days: form.value.days.map(({ acceptance_text, ...day }) => ({ ...day, acceptance_criteria: acceptance_text.split('\n').map(item => item.trim()).filter(Boolean) })),
  }
  try {
    const plan = await api(editing.value ? `/my-plans/${route.params.slug}/` : '/my-plans/', { method: editing.value ? 'PUT' : 'POST', body: JSON.stringify(payload) })
    router.push(`/plans/${plan.slug}`)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="loading" />
    <div v-else class="page-enter plan-editor">
      <header class="page-heading compact"><div><h1>{{ editing ? '编辑学习路线' : '创建自己的学习路线' }}</h1><p>先定义结果，再把它拆成每天可完成、可验收的任务。</p></div></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <form class="editor-form" @submit.prevent="save">
        <section class="editor-section">
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
        <footer class="editor-actions"><span>保存后可以先加入自己的路径，也可以提交管理员审核后公开。</span><button class="button primary" :disabled="busy">{{ busy ? '正在保存' : '保存学习路线' }}</button></footer>
      </form>
    </div>
  </AppShell>
</template>
