<script setup>
import { nextTick, onMounted, ref } from 'vue'

import { api } from '../api'
import LoadingState from './LoadingState.vue'

const props = defineProps({
  slug: { type: String, required: true },
  dayNumber: { type: Number, required: true },
  planTitle: { type: String, default: '' },
})
const emit = defineEmits(['close', 'saved'])

// 一个知识点有 17 个字段，按学习顺序分四组折叠，避免一屏塞满输入框。
const GROUPS = [
  ['基础信息', [['name', '名称'], ['summary', '一句话说明'], ['what_it_solves', '解决什么问题'], ['role', '在体系中的角色']]],
  ['原理与工具', [['basic', '基础概念', 'text'], ['mechanism', '运行机制', 'text'], ['tools', '相关工具', 'lines'], ['pitfalls', '常见坑', 'lines']]],
  ['实现', [['implementation_requirement', '实现要求', 'text'], ['language', '语言'], ['run_command', '运行命令'], ['expected_results', '预期结果', 'lines'], ['code_explanation', '代码讲解', 'lines']]],
  ['学习支持', [['mastery', '掌握标准', 'lines'], ['practice_steps', '练习步骤', 'lines'], ['resources', '延伸资料（每行「标题 | 链接」）', 'lines']]],
]
const LIST_FIELDS = ['tools', 'pitfalls', 'expected_results', 'code_explanation', 'mastery', 'practice_steps']

const dialog = ref(null)
const day = ref(null)
const form = ref(null)
const error = ref('')
const notice = ref('')
const busy = ref(false)

onMounted(async () => {
  await nextTick()
  if (!dialog.value.open) dialog.value.showModal()
  try {
    load(await api(`/admin/plan-reviews/${props.slug}/day/?number=${props.dayNumber}`))
  } catch (err) { error.value = err.message }
})

// 表单里所有列表字段都用「一行一项」的文本编辑，保存时再拆回数组。
const toLines = (value) => (value || []).map((item) => (typeof item === 'string' ? item : `${item.title || ''} | ${item.url || ''}`)).join('\n')
const fromLines = (value) => (value || '').split('\n').map((line) => line.trim()).filter(Boolean)

function load(data) {
  // content_edited_at 在响应外层，合进来给页脚提示用。
  day.value = { ...data.day, content_edited_at: data.content_edited_at }
  form.value = {
    title: data.day.title,
    core_knowledge: data.day.core_knowledge,
    hands_on_task: data.day.hands_on_task,
    estimated_minutes: data.day.estimated_minutes,
    reference_answer: data.day.reference_answer,
    acceptance_criteria: toLines(data.day.acceptance_criteria),
    commands: toLines(data.day.commands),
    knowledge_details: (data.day.knowledge_details || []).map(unpack),
  }
}

function unpack(item) {
  const point = { ...item }
  for (const field of LIST_FIELDS) point[field] = toLines(item[field])
  point.resources = toLines(item.resources)
  return point
}

function pack(point) {
  const item = { ...point }
  for (const field of LIST_FIELDS) item[field] = fromLines(point[field])
  item.resources = fromLines(point.resources).map((line) => {
    const [title, url = ''] = line.split('|')
    return { title: title.trim(), url: url.trim() }
  })
  return item
}

function addPoint() {
  form.value.knowledge_details.push(unpack({ name: '', summary: '', language: 'python' }))
}

function removePoint(index) {
  if (form.value.knowledge_details.length === 1) return (error.value = '至少保留一个知识点。')
  if (confirm(`删除知识点“${form.value.knowledge_details[index].name || '未命名'}”？保存后不可恢复。`)) form.value.knowledge_details.splice(index, 1)
}

async function save() {
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    const data = await api(`/admin/plan-reviews/${props.slug}/day/?number=${props.dayNumber}`, {
      method: 'PATCH',
      body: JSON.stringify({
        ...form.value,
        estimated_minutes: Number(form.value.estimated_minutes) || 0,
        acceptance_criteria: fromLines(form.value.acceptance_criteria),
        commands: fromLines(form.value.commands),
        knowledge_details: form.value.knowledge_details.map(pack),
      }),
    })
    load(data)
    notice.value = '正文已保存，学习者下次打开这一天就是新内容。'
    emit('saved', data.day)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

function close() {
  if (dialog.value?.open) dialog.value.close()
  emit('close')
}
</script>

<template>
  <dialog ref="dialog" class="knowledge-dialog" @click.self="close" @close="emit('close')">
    <article class="knowledge-drawer day-editor">
      <header>
        <div>
          <span class="eyebrow">{{ planTitle }} · DAY {{ dayNumber }}</span>
          <h2>{{ day?.title || '加载中…' }}</h2>
          <p>{{ day?.week_title }}{{ day?.week_title ? ' · ' : '' }}正文与知识点直接存在数据库里，保存后立即对学习者生效。</p>
        </div>
        <button aria-label="关闭学习日正文" @click="close">×</button>
      </header>
      <div class="knowledge-scroll">
        <p v-if="error" class="notice error">{{ error }}</p>
        <p v-if="notice" class="notice success">{{ notice }}</p>
        <LoadingState v-if="!form" />
        <template v-else>
          <section>
            <span class="detail-label">这一天</span>
            <label>标题<input v-model.trim="form.title" maxlength="200" /></label>
            <label>核心知识<textarea v-model.trim="form.core_knowledge" rows="3"></textarea></label>
            <label>实践任务<textarea v-model.trim="form.hands_on_task" rows="3"></textarea></label>
            <label>验收标准（每行一条）<textarea v-model="form.acceptance_criteria" rows="4"></textarea></label>
            <label>预计时长（分钟）<input v-model="form.estimated_minutes" type="number" min="1" max="600" /></label>
            <label>验证命令（每行一条）<textarea v-model="form.commands" rows="3"></textarea></label>
          </section>
          <section>
            <span class="detail-label">参考实现</span>
            <p>参考代码按知识点保存；展开后可直接检查和修改。</p>
            <details v-for="(point, index) in form.knowledge_details" :key="`reference-${index}`" :open="index === 0">
              <summary>{{ point.name || `知识点 ${index + 1}` }}</summary>
              <label>
                参考代码
                <textarea v-model="point.reference_code" class="code-input" rows="8" placeholder="暂未填写该知识点的参考代码"></textarea>
              </label>
            </details>
            <details :open="!!form.reference_answer">
              <summary>当天综合参考实现（可选）</summary>
              <label>
                综合参考代码
                <textarea v-model="form.reference_answer" class="code-input" rows="8" placeholder="需要提供跨知识点的完整实现时填写"></textarea>
              </label>
            </details>
          </section>
          <section v-for="(point, index) in form.knowledge_details" :key="index" class="knowledge-edit">
            <div class="knowledge-edit-head">
              <span class="detail-label">知识点 {{ index + 1 }} · {{ point.name || '未命名' }}</span>
              <button class="text-action" @click="removePoint(index)">删除</button>
            </div>
            <details v-for="([groupTitle, fields], groupIndex) in GROUPS" :key="groupTitle" :open="groupIndex === 0">
              <summary>{{ groupTitle }}</summary>
              <label v-for="[field, label, kind] in fields" :key="field">
                {{ label }}
                <input v-if="!kind" v-model.trim="point[field]" />
                <textarea v-else v-model="point[field]" :class="{ 'code-input': kind === 'code' }" :rows="kind === 'code' ? 8 : 3"></textarea>
              </label>
            </details>
          </section>
          <section>
            <span class="detail-label">知识点</span>
            <p>共 {{ form.knowledge_details.length }} 个。学习者需要逐个确认掌握，才能完成这一天。</p>
            <button class="button ghost" @click="addPoint">＋ 新增知识点</button>
          </section>
          <section v-if="day.community_supplements?.length">
            <span class="detail-label">社区共建补充（在课程共建栏审核）</span>
            <div v-for="item in day.community_supplements" :key="item.title"><b>{{ item.title }}</b><p>{{ item.content }}</p></div>
          </section>
        </template>
      </div>
      <footer>
        <span>{{ day?.content_edited_at ? '已手工编辑，重新导入系统路线时会跳过这一天' : '尚未手工编辑' }}</span>
        <button class="button secondary" @click="close">关闭</button>
        <button class="button primary" :disabled="busy || !form" @click="save">保存正文</button>
      </footer>
    </article>
  </dialog>
</template>
