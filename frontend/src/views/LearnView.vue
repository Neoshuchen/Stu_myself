<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'
import { pastedImages, resizeUploadImage } from '../image'
import { useUnsavedChanges } from '../useUnsavedChanges'

const route = useRoute()
const router = useRouter()
const progress = ref(null)
const error = ref('')
const notice = ref('')
const busy = ref(false)
const pendingSaves = ref(0)
const saveError = ref('')
const savedProgress = ref('')
const markingKnowledge = ref(false)
const showReference = ref(false)
const knowledgeDialog = ref(null)
const selectedKnowledge = ref(null)
const selectedKnowledgeIndex = ref(-1)
const evidenceForm = ref({ kind: 'test', title: '', content: '', url: '', attachment: null })
const evidenceFileInput = ref(null)
const evidenceError = ref('')
const preparingEvidence = ref(false)
const gapForm = ref({ title: '', detail: '' })
const gapResolutions = reactive({})
const sessionMinutes = ref(15)
let saveQueue = Promise.resolve()
let loadVersion = 0
// 与后端完成规则一致：已配置的项目必须全部通过，空项目列表不产生虚假的“还差 0 项”。
const checksComplete = computed(() => progress.value?.acceptance_checks.every(Boolean))
const knowledgeComplete = computed(() => progress.value?.knowledge_checks.every(Boolean))
const canComplete = computed(() => knowledgeComplete.value && checksComplete.value && progress.value?.evidence.length > 0 && !pendingSaves.value && !saveError.value)
const progressDirty = computed(() => progress.value && JSON.stringify(progressPayload(progress.value)) !== savedProgress.value)
const dirty = computed(() => Boolean(progressDirty.value || pendingSaves.value || preparingEvidence.value
  || evidenceForm.value.title || evidenceForm.value.content || evidenceForm.value.url || evidenceForm.value.attachment
  || gapForm.value.title || gapForm.value.detail
  || progress.value?.gaps.some(gap => gapResolutions[gap.id] && gapResolutions[gap.id] !== gap.resolution)))
useUnsavedChanges(dirty)
const missingSteps = computed(() => {
  if (!progress.value) return []
  return [
    !knowledgeComplete.value && { id: 'lesson-knowledge', label: `还需学习 ${progress.value.knowledge_checks.filter(value => !value).length} 个知识点` },
    !checksComplete.value && { id: 'lesson-checkpoint', label: `还需完成 ${progress.value.acceptance_checks.filter(value => !value).length} 项验收` },
    !progress.value.evidence.length && { id: 'lesson-evidence', label: '还需提交 1 项学习证据' },
  ].filter(Boolean)
})
const daySections = computed(() => Array.isArray(progress.value?.day.content) ? progress.value.day.content : progress.value?.day.content?.workflow || [])
const knowledgeDetails = computed(() => progress.value?.day.knowledge_details || [])
const lessonContent = computed(() => Array.isArray(progress.value?.day.content) ? {} : progress.value?.day.content || {})
const prerequisites = computed(() => lessonContent.value.prerequisites || [])
const learningObjectives = computed(() => lessonContent.value.learning_objectives || [])
const conceptMap = computed(() => lessonContent.value.concept_map || [])
const comprehensiveTask = computed(() => lessonContent.value.comprehensive_task || null)
const verification = computed(() => lessonContent.value.verification || null)
const nextKnowledgeIndex = computed(() => progress.value?.knowledge_checks.findIndex(value => !value) ?? -1)
const nextCriterion = computed(() => progress.value?.day.acceptance_criteria.find((_item, index) => !progress.value.acceptance_checks[index]))
const sessionTask = computed(() => {
  const next = knowledgeDetails.value[nextKnowledgeIndex.value]
  if (sessionMinutes.value === 60) return nextCriterion.value || '整理本日实验结果，保存一份可核对的学习证据。'
  if (!next) return nextCriterion.value || '闭卷回顾今天的主题，写下仍不确定的问题。'
  return sessionMinutes.value === 15 ? `用自己的话解释“${next.name}”，再核对一个具体例子。` : next.implementation_requirement
})
const shareLink = computed(() => {
  if (!progress.value) return '/community/new'
  const params = new URLSearchParams({ day: progress.value.day.day_number, type: 'check_in' })
  if (progress.value.reflection) params.set('content', progress.value.reflection)
  return `/plans/${progress.value.day.plan_slug || ''}/community/new?${params}`
})

async function load() {
  const version = ++loadVersion
  error.value = ''
  progress.value = null
  saveError.value = ''
  evidenceForm.value = { kind: 'test', title: '', content: '', url: '', attachment: null }
  gapForm.value = { title: '', detail: '' }
  Object.keys(gapResolutions).forEach(key => delete gapResolutions[key])
  closeKnowledge()
  try {
    let loaded = await api(`/enrollments/${route.params.enrollmentId}/day/?number=${route.params.dayNumber}`)
    loaded = await api(`/progress/${loaded.id}/start/`, { method: 'POST' })
    if (version === loadVersion) {
      progress.value = loaded
      savedProgress.value = JSON.stringify(progressPayload(loaded))
    }
  } catch (err) { if (version === loadVersion) error.value = err.message }
}

onMounted(load)
watch(() => [route.params.enrollmentId, route.params.dayNumber], load)

/** 提取指定进度的可保存字段，返回独立快照，供写入和未保存检测共用。 */
function progressPayload(current) {
  return {
    acceptance_checks: [...current.acceptance_checks],
    knowledge_checks: [...current.knowledge_checks],
    reflection: current.reflection,
    resume_note: current.resume_note,
    recall_score: current.recall_score,
  }
}

/** 排队保存进度快照；changes 可覆盖本次字段，strict 控制失败是否抛出，返回保存结果或 null。 */
function saveProgress(message = '学习记录已保存', strict = false, changes = {}) {
  const current = progress.value
  const payload = progressPayload(current)
  pendingSaves.value += 1
  saveError.value = ''
  notice.value = ''
  const request = saveQueue.then(async () => {
    // 知识状态只在成功后更新；后续排队的普通保存必须沿用已确认的状态，避免旧快照撤销它。
    Object.assign(payload, { knowledge_checks: [...current.knowledge_checks] }, changes)
    const saved = await api(`/progress/${current.id}/`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    })
    current.knowledge_checks = saved.knowledge_checks
    if (progress.value === current) {
      savedProgress.value = JSON.stringify(payload)
      saveError.value = ''
      if (message) {
        notice.value = message
        setTimeout(() => { if (notice.value === message) notice.value = '' }, 1800)
      }
    }
    return saved
  }).catch((err) => {
    if (progress.value === current) saveError.value = err.message
    throw err
  }).finally(() => {
    pendingSaves.value -= 1
  })
  saveQueue = request.catch(() => null)
  return strict ? request : saveQueue
}

async function addEvidence() {
  const current = progress.value
  evidenceError.value = ''
  const form = new FormData()
  form.append('progress', progress.value.id)
  Object.entries(evidenceForm.value).forEach(([key, value]) => { if (value) form.append(key, value) })
  busy.value = true
  try {
    const saved = await api('/evidence/', { method: 'POST', body: form })
    // 子记录只更新自己的列表，不能用服务端旧快照覆盖仍在保存的学习草稿。
    current.evidence.unshift(saved)
    if (progress.value !== current) return
    evidenceForm.value = { kind: 'test', title: '', content: '', url: '', attachment: null }
    if (evidenceFileInput.value) evidenceFileInput.value.value = ''
    notice.value = '证据已收好'
  } catch (err) { evidenceError.value = err.message } finally { busy.value = false }
}

async function removeEvidence(id) {
  const current = progress.value
  busy.value = true
  try {
    await saveProgress('', true)
    await api(`/evidence/${id}/`, { method: 'DELETE' })
    current.evidence = current.evidence.filter(item => item.id !== id)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 切换本人证据的私人成果展柜选择；失败时保留当前界面状态。 */
async function featureEvidence(item) {
  busy.value = true
  try {
    const saved = await api(`/evidence/${item.id}/feature/`, { method: 'POST', body: JSON.stringify({ is_featured: !item.is_featured }) })
    item.is_featured = saved.is_featured
    notice.value = saved.is_featured ? '已选入私人成果展柜，可在学习洞察中查看' : '已移出成果展柜'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 下载固定实验的源码与断言，供用户在本地 Python 中复现和修复。 */
function downloadLab() {
  const lab = progress.value.day.lab
  const text = `# ${lab.title}\n# ${lab.brief}\n# 修复函数后运行：python ${lab.id}.py（不要使用 -O，否则会跳过断言）\n\n${lab.starter}\n${lab.checks}\nprint("全部检查通过，请再补充自己的边界样例。")\n`
  const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `${lab.id}.py`
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

/** 把案件验收要求放入现有证据表单草稿，等待用户填写实际结果并提交。 */
function prepareLabEvidence() {
  if ((evidenceForm.value.title || evidenceForm.value.content) && !confirm('用案件记录模板替换当前未提交的证据文字？')) return
  evidenceForm.value.title = progress.value.day.lab.title
  evidenceForm.value.kind = 'test'
  evidenceForm.value.content = '复现命令与环境：\n修复前的失败输出：\n根因：\n修改说明：\n修复后的检查输出：\n我补充的边界样例：'
  focusLessonSection('lesson-evidence')
}

/** 将焦点移至指定区域；参数为学习区 ID，无返回值，同时兼容桌面分栏与手机整页滚动。 */
function focusLessonSection(id) {
  const section = document.getElementById(id)
  section?.scrollIntoView({ block: 'start' })
  section?.focus({ preventScroll: true })
}

/** 把选中知识点作为待确认的 AI 上下文，打开抽屉但不发送请求给模型。 */
function askAboutKnowledge() {
  const item = selectedKnowledge.value
  const detail = {
    title: item.name.slice(0, 160),
    content: [`主题：${item.name}`, item.summary, item.basic, item.mechanism, `练习要求：${item.implementation_requirement}`].join('\n\n').slice(0, 4000),
  }
  closeKnowledge()
  window.dispatchEvent(new CustomEvent('open-ai-focus', { detail }))
}

async function addGap() {
  const current = progress.value
  busy.value = true
  try {
    const saved = await api('/gaps/', { method: 'POST', body: JSON.stringify({ progress: current.id, ...gapForm.value }) })
    current.gaps.unshift(saved)
    if (progress.value !== current) return
    gapForm.value = { title: '', detail: '' }
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function requestGapVerification(gap) {
  const current = progress.value
  busy.value = true
  error.value = ''
  try {
    const saved = await api(`/gaps/${gap.id}/request-verification/`, {
      method: 'POST',
      body: JSON.stringify({ resolution: gapResolutions[gap.id] || gap.resolution || '' }),
    })
    current.gaps = current.gaps.map(item => item.id === saved.id ? saved : item)
    if (progress.value !== current) return
    notice.value = '已邀请小队朋友验证这个缺口'
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

async function completeDay() {
  busy.value = true
  error.value = ''
  try {
    await saveProgress('', true)
    await api(`/progress/${progress.value.id}/complete/`, { method: 'POST' })
    router.push({ path: '/dashboard', query: { enrollment: route.params.enrollmentId } })
  } catch (err) { error.value = err.message } finally { busy.value = false }
}

/** 准备一个证据附件；选择文件和粘贴图片共用同一缩放与错误处理。 */
async function prepareEvidenceAttachment(file) {
  evidenceError.value = ''
  evidenceForm.value.attachment = null
  preparingEvidence.value = true
  try {
    evidenceForm.value.attachment = await resizeUploadImage(file)
    return true
  } catch (err) {
    evidenceError.value = err.message || '无法读取图片，请更换文件后重试。'
    return false
  } finally {
    preparingEvidence.value = false
  }
}

/** 读取文件选择器中的附件，并允许再次选择同名文件。 */
async function fileChanged(event) {
  const file = event.target.files[0] || null
  if (file) await prepareEvidenceAttachment(file)
  event.target.value = ''
}

/** 把说明框内粘贴的第一张图片作为证据附件，普通文字仍按原方式粘贴。 */
async function evidenceImagePasted(event) {
  const image = pastedImages(event)[0]
  if (!image) return
  event.preventDefault()
  await prepareEvidenceAttachment(image)
}

/** 移除尚未提交的证据附件。 */
function clearEvidenceAttachment() {
  evidenceForm.value.attachment = null
  evidenceError.value = ''
}

async function openKnowledge(item, index) {
  selectedKnowledge.value = item
  selectedKnowledgeIndex.value = index
  await nextTick()
  knowledgeDialog.value.showModal()
}

function closeKnowledge() {
  if (knowledgeDialog.value?.open) knowledgeDialog.value.close()
  selectedKnowledge.value = null
  selectedKnowledgeIndex.value = -1
}

/** 保存选中知识点后关闭详情；失败保留详情和原状态，允许重试，无参数和返回值。 */
async function markKnowledgeComplete() {
  if (markingKnowledge.value) return
  const index = selectedKnowledgeIndex.value
  markingKnowledge.value = true
  try {
    if (!progress.value.knowledge_checks[index]) {
      const checks = [...progress.value.knowledge_checks]
      checks[index] = true
      const saved = await saveProgress('知识点学习状态已保存', false, { knowledge_checks: checks })
      if (!saved) return
    }
    if (selectedKnowledgeIndex.value === index) closeKnowledge()
  } finally {
    markingKnowledge.value = false
  }
}

async function copyReference() {
  await navigator.clipboard.writeText(selectedKnowledge.value.reference_code)
  notice.value = '参考实现已复制，请先独立复现再核对'
}

async function requestPeerReview() {
  busy.value = true
  try {
    await api('/peer-reviews/', { method: 'POST', body: JSON.stringify({ progress: progress.value.id }) })
    notice.value = '已进入同路线互评池'
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!progress && !error" />
    <p v-else-if="error && !progress" class="notice error">{{ error }}</p>
    <div v-else class="learn-page page-enter">
      <RouterLink class="lesson-back" :to="{ path: '/journey', query: { enrollment: route.params.enrollmentId } }">← 返回学习路径</RouterLink>
      <header class="lesson-heading">
        <div class="lesson-index"><span>DAY</span><strong>{{ progress.day.day_number }}</strong></div>
        <div><span class="eyebrow">{{ progress.day.phase }} / 第 {{ progress.day.week_number }} 周</span><h1>{{ progress.day.title }}</h1><p>{{ progress.day.week_title }}</p></div>
        <div class="lesson-time"><b>{{ progress.day.estimated_minutes }}</b><span>分钟</span></div>
      </header>
      <nav class="lesson-jumps" aria-label="本日学习导航">
        <button @click="focusLessonSection('lesson-knowledge')">知识点 <span>{{ progress.knowledge_checks.filter(Boolean).length }}/{{ progress.knowledge_checks.length }}</span></button>
        <button @click="focusLessonSection('lesson-checkpoint')">当日验收 <span>{{ progress.acceptance_checks.filter(Boolean).length }}/{{ progress.acceptance_checks.length }}</span></button>
        <button @click="focusLessonSection('lesson-evidence')">学习证据 <span>{{ progress.evidence.length }}</span></button>
      </nav>

      <div v-if="notice" class="toast">{{ notice }}</div>
      <p v-if="error" class="notice error">{{ error }}</p>

      <div class="lesson-layout">
        <article class="lesson-content" tabindex="0" aria-label="学习正文">
          <section class="task-callout"><div><span class="eyebrow">最终复现任务</span><h2>{{ progress.day.hands_on_task }}</h2></div></section>
          <section class="panel short-study" aria-label="短时学习">
            <div class="section-title"><h2>今天先学一小段</h2><label>可用时间 <select v-model.number="sessionMinutes"><option :value="15">15 分钟</option><option :value="30">30 分钟</option><option :value="60">60 分钟</option></select></label></div>
            <p>{{ sessionTask }}</p>
            <button v-if="nextKnowledgeIndex >= 0 && sessionMinutes !== 60" class="button secondary" @click="openKnowledge(knowledgeDetails[nextKnowledgeIndex], nextKnowledgeIndex)">打开下一个知识点</button>
            <details class="resume-note">
              <summary>{{ progress.resume_note ? '查看或修改接续提示' : '留下接续提示' }}</summary>
              <label>下次从这里继续<textarea v-model="progress.resume_note" maxlength="500" rows="2" placeholder="例如：已复现正常输入，下次补充空列表测试。" @change="saveProgress('接续提示已保存')"></textarea></label>
              <button class="button ghost" :disabled="busy" @click="saveProgress('本段记录已保存，下次可从接续提示继续')">保存本段进度</button>
            </details>
            <small>完成整日仍需全部知识点、验收项和至少一份证据。</small>
          </section>

          <section v-if="prerequisites.length || learningObjectives.length" class="lesson-orientation">
            <div v-if="prerequisites.length"><span class="eyebrow">开始前应具备</span><ul><li v-for="item in prerequisites" :key="item">{{ item }}</li></ul></div>
            <div v-if="learningObjectives.length"><span class="eyebrow">学完后你能够</span><ul><li v-for="item in learningObjectives" :key="item">{{ item }}</li></ul></div>
          </section>

          <section id="lesson-knowledge" class="content-section" tabindex="-1" aria-label="本日知识点">
            <div class="section-number">01</div><div><h2>今天要掌握什么</h2>
              <p class="lead">{{ progress.day.core_knowledge }}</p>
              <div v-if="conceptMap.length" class="concept-map">
                <div v-for="concept in conceptMap" :key="concept.term"><b>{{ concept.term }}</b><p>{{ concept.explanation }}</p></div>
              </div>
              <div class="knowledge-grid">
                <article v-for="(item, index) in knowledgeDetails" :key="item.name" :class="['knowledge-card', { learned: progress.knowledge_checks[index] }]">
                  <div><span>{{ String(index + 1).padStart(2, '0') }}</span><i>{{ progress.knowledge_checks[index] ? '✓ 已学习' : '待学习' }}</i></div>
                  <h3>{{ item.name }}</h3><p>{{ item.summary }}</p>
                  <button @click="openKnowledge(item, index)">详细学习</button>
                </article>
              </div>
            </div>
          </section>

          <section v-if="progress.day.lab" class="panel detective-lab">
            <span class="eyebrow">动手实验</span><h2>{{ progress.day.lab.title }}</h2><p>{{ progress.day.lab.brief }}</p>
            <ol><li>下载案件，在本地运行并保留失败输出。</li><li>说明根因，修复函数并保留检查项。</li><li>全部检查通过后，再补一个边界样例并提交证据。</li></ol>
            <div class="button-row"><button class="button secondary" @click="downloadLab">下载 Python 案件</button><button class="button ghost" @click="prepareLabEvidence">填写案件证据</button></div>
            <details><summary>我已尝试，查看线索</summary><p>{{ progress.day.lab.hint }}</p><details><summary>核对修复思路</summary><p>{{ progress.day.lab.solution }}</p></details></details>
          </section>

          <section v-for="(block, index) in daySections" :key="block.title" class="content-section">
            <div class="section-number">{{ String(index + 2).padStart(2, '0') }}</div><div><h2>{{ block.title }}</h2><p class="content-body">{{ block.body }}</p></div>
          </section>

          <section v-if="comprehensiveTask" class="content-section comprehensive-task">
            <div class="section-number">任务</div><div>
              <h2>独立综合任务</h2><h3>{{ comprehensiveTask.goal }}</h3>
              <dl><div><dt>固定输入</dt><dd>{{ comprehensiveTask.input }}</dd></div><div><dt>应交付输出</dt><dd>{{ comprehensiveTask.output }}</dd></div></dl>
              <h4>实现约束</h4><ul><li v-for="item in comprehensiveTask.requirements" :key="item">{{ item }}</li></ul>
              <h4>必须验证的失败路径</h4><ul><li v-for="item in comprehensiveTask.error_cases" :key="item">{{ item }}</li></ul>
            </div>
          </section>

          <section v-if="verification" class="content-section verification-section">
            <div class="section-number">验证</div><div><h2>测试与学习证据</h2>
              <div class="verification-columns"><div><h4>完成检查</h4><ul><li v-for="item in verification.checks" :key="item">{{ item }}</li></ul></div><div><h4>需要提交</h4><ul><li v-for="item in verification.evidence" :key="item">{{ item }}</li></ul></div></div>
            </div>
          </section>

          <section v-if="progress.day.commands.length" class="content-section">
            <div class="section-number">执行</div><div><h2>运行与验证</h2><pre v-for="command in progress.day.commands" :key="command"><code>{{ command }}</code></pre></div>
          </section>

          <section class="reference-box">
            <button @click="showReference = !showReference"><span><small>先独立尝试，再核对思路</small><b>参考实现与提示</b></span><i>{{ showReference ? '−' : '+' }}</i></button>
            <div v-if="showReference" class="reference-body">
              <pre v-if="progress.day.reference_answer"><code>{{ progress.day.reference_answer }}</code></pre>
              <p v-else>本日以独立实验和验收证据为准。详细参考实现可由管理员在课程后台补充；遇到具体阻塞时，请把问题缩小到输入、输出和失败证据后再求助。</p>
            </div>
          </section>

          <section v-if="progress.day.community_supplements.length" class="community-supplements"><span class="eyebrow">社区共建补充</span><article v-for="item in progress.day.community_supplements" :key="`${item.title}-${item.author}`"><h3>{{ item.title }}</h3><p>{{ item.content }}</p><small>贡献者：{{ item.author }}</small></article></section>

          <section class="reflection-box">
            <h2>用自己的话收尾</h2><p>今天的知识解决了什么？哪些结论已经证实，哪些仍是推测？</p>
            <textarea v-model="progress.reflection" rows="5" placeholder="写下你的复盘，不需要漂亮，只需要具体……" @change="saveProgress('复盘已自动保存')"></textarea>
            <div class="score-row"><label>闭卷掌握度 <input v-model.number="progress.recall_score" type="range" min="0" max="100" step="10" @change="saveProgress('掌握度已自动保存')" /><b>{{ progress.recall_score ?? 0 }}%</b></label><div class="button-row"><RouterLink class="button secondary" :to="shareLink">分享到学习小组</RouterLink></div></div>
          </section>
        </article>

        <aside class="lesson-sidebar" tabindex="0" aria-label="学习进度与证据提交">
          <section class="panel knowledge-progress-card">
            <div><h2>知识学习</h2></div><strong>{{ progress.knowledge_checks.filter(Boolean).length }}/{{ progress.knowledge_checks.length }}</strong>
            <div class="completion-meter"><i :style="{ width: `${progress.knowledge_checks.filter(Boolean).length / progress.knowledge_checks.length * 100 || 0}%` }"></i></div>
            <p>打开详情，完成最小复现后再标记学习。</p>
          </section>
          <section id="lesson-checkpoint" class="panel checkpoint-card" tabindex="-1" aria-label="当日验收">
            <h2>当日验收</h2><p>全部完成并提交至少一项证据，才算真正结束。</p>
            <label v-for="(item, index) in progress.day.acceptance_criteria" :key="item" class="check-row">
              <input v-model="progress.acceptance_checks[index]" type="checkbox" @change="saveProgress('验收状态已保存')" /><span><i>✓</i>{{ item }}</span>
            </label>
            <div class="completion-meter"><i :style="{ width: `${progress.acceptance_checks.filter(Boolean).length / progress.acceptance_checks.length * 100 || 0}%` }"></i></div>
          </section>

          <section id="lesson-evidence" class="panel evidence-card" tabindex="-1" aria-label="学习证据">
            <div class="section-title mini"><h2>学习证据</h2><span>{{ progress.evidence.length }}</span></div>
            <div v-if="progress.evidence.length" class="evidence-list">
              <div v-for="item in progress.evidence" :key="item.id" class="evidence-item"><div><b>{{ item.title }}</b><small>{{ item.kind }} · {{ new Date(item.created_at).toLocaleDateString('zh-CN') }}</small><a v-if="item.url" :href="item.url" target="_blank" rel="noopener">查看链接</a><a v-if="item.attachment_url" :href="item.attachment_url" target="_blank" rel="noopener"><img v-if="item.attachment_is_image" :src="item.attachment_url" :alt="item.title" loading="lazy" /><span v-else>查看附件 {{ item.attachment_name }}</span></a><button type="button" class="text-action" :disabled="busy" :aria-pressed="item.is_featured" @click="featureEvidence(item)">{{ item.is_featured ? '★ 已选入展柜' : '☆ 选入私人成果展柜' }}</button></div><button aria-label="删除证据" :disabled="busy" @click="removeEvidence(item.id)">×</button></div>
            </div>
            <form class="mini-form" @submit.prevent="addEvidence">
              <div class="form-pair"><select v-model="evidenceForm.kind"><option value="test">测试结果</option><option value="commit">Git提交</option><option value="code">代码</option><option value="log">日志</option><option value="report">报告</option><option value="link">链接</option><option value="note">笔记</option></select><input v-model.trim="evidenceForm.title" required placeholder="证据标题" /></div>
              <textarea v-model.trim="evidenceForm.content" rows="3" placeholder="粘贴关键输出或说明；可直接 Ctrl+V 粘贴图片" @paste="evidenceImagePasted"></textarea><input v-model.trim="evidenceForm.url" type="url" placeholder="https:// 可选链接" />
              <label class="file-input"><input ref="evidenceFileInput" type="file" accept="image/png,image/jpeg,image/webp,text/plain,application/json,application/pdf" @change="fileChanged" /><span>{{ preparingEvidence ? '正在处理图片…' : evidenceForm.attachment?.name || '添加附件（图片自动压缩至8MB内，其他附件最大10MB）' }}</span></label>
              <button v-if="evidenceForm.attachment" type="button" class="text-action" :disabled="preparingEvidence" :aria-label="`移除附件 ${evidenceForm.attachment.name}`" @click="clearEvidenceAttachment">移除已选附件</button>
              <p v-if="evidenceError" class="form-error" role="alert">{{ evidenceError }}</p>
              <button class="button secondary wide" :disabled="busy || preparingEvidence">提交证据</button>
            </form>
          </section>

          <section class="panel gap-card">
            <h2>具体缺口</h2>
            <ul v-if="progress.gaps.length" class="gap-list"><li v-for="gap in progress.gaps" :key="gap.id"><i></i><span><b>{{ gap.title }}</b><small>{{ gap.detail }}</small><em v-if="gap.status === 'verifying'">等待朋友验证 · {{ gap.resolution }}</em><em v-else-if="gap.status === 'resolved'">✓ {{ gap.verified_by_name ? `${gap.verified_by_name} 已验证` : '已解决' }}{{ gap.verification_note ? ` · ${gap.verification_note}` : '' }}</em><template v-else><em v-if="gap.verification_note">上次验证反馈：{{ gap.verification_note }}</em><textarea v-model.trim="gapResolutions[gap.id]" rows="2" maxlength="2000" placeholder="写下你如何复现、修复并确认结果"></textarea><button class="text-action" :disabled="busy || !progress.evidence.length" @click="requestGapVerification(gap)">邀请小队朋友验证</button></template></span></li></ul>
            <form class="mini-form" @submit.prevent="addGap"><input v-model.trim="gapForm.title" required placeholder="例如：无法解释取消传播" /><textarea v-model.trim="gapForm.detail" rows="2" placeholder="具体卡在哪里？"></textarea><button class="text-action" :disabled="busy">记录缺口</button></form>
          </section>

          <section class="panel completion-status" aria-label="完成条件与保存状态">
            <h2>完成今天</h2>
            <ul v-if="missingSteps.length && progress.status !== 'completed'" class="completion-steps">
              <li v-for="step in missingSteps" :key="step.id"><button class="text-action" @click="focusLessonSection(step.id)">{{ step.label }} →</button></li>
            </ul>
            <p v-else>{{ progress.status === 'completed' ? '今天的学习已完成。' : '知识、验收和证据已齐备。' }}</p>
            <p class="save-status" role="status">{{ pendingSaves ? '正在保存…' : saveError ? '保存失败，内容仍保留在本页' : progressDirty ? '有尚未保存的修改' : '学习记录已保存' }}</p>
            <p v-if="saveError" class="notice error" role="alert">{{ saveError }}</p>
            <button v-if="saveError || progressDirty" class="button secondary wide" :disabled="pendingSaves > 0" @click="saveProgress()">{{ saveError ? '重试保存' : '保存学习记录' }}</button>
          </section>
          <button class="button finish wide" :disabled="!canComplete || busy || progress.status === 'completed'" @click="completeDay">
            {{ progress.status === 'completed' ? '今天已经完成' : pendingSaves ? '正在保存学习记录…' : saveError ? '请先重试保存' : canComplete ? '完成今天，继续前进' : '请先完成上方待办' }}
          </button>
          <button class="button ghost wide" :disabled="!progress.evidence.length || busy" @click="requestPeerReview">邀请同路线学习者互评</button>
        </aside>
      </div>

      <dialog ref="knowledgeDialog" class="knowledge-dialog" @click.self="closeKnowledge" @close="selectedKnowledge = null">
        <article v-if="selectedKnowledge" class="knowledge-drawer">
          <header>
            <div><span class="eyebrow">知识点 {{ String(selectedKnowledgeIndex + 1).padStart(2, '0') }}</span><h2>{{ selectedKnowledge.name }}</h2><p>{{ selectedKnowledge.summary }}</p></div>
            <button aria-label="关闭知识详情" @click="closeKnowledge">×</button>
          </header>
          <div class="knowledge-scroll">
            <section v-if="selectedKnowledge.what_it_solves" class="detail-purpose"><span class="detail-label">它到底解决什么问题</span><p>{{ selectedKnowledge.what_it_solves }}</p></section>
            <section><span class="detail-label">基础知识</span><p>{{ selectedKnowledge.basic }}</p></section>
            <section><span class="detail-label">核心运行机制</span><p>{{ selectedKnowledge.mechanism }}</p><div class="tool-row"><span v-for="tool in selectedKnowledge.tools" :key="tool">{{ tool }}</span></div></section>
            <section class="detail-role"><span class="detail-label">在今日任务中的作用</span><p>{{ selectedKnowledge.role }}</p></section>
            <section><span class="detail-label">常见错误与边界</span><ul><li v-for="pitfall in selectedKnowledge.pitfalls" :key="pitfall">{{ pitfall }}</li></ul></section>
            <section><span class="detail-label">代码 / 实验实现要求</span><p>{{ selectedKnowledge.implementation_requirement }}</p></section>
            <section v-if="selectedKnowledge.practice_steps?.length"><span class="detail-label">建议复现顺序</span><ol class="practice-steps"><li v-for="(step, index) in selectedKnowledge.practice_steps" :key="step"><b>{{ index + 1 }}</b><span>{{ step }}</span></li></ol></section>
            <section v-if="selectedKnowledge.reference_code" class="code-detail">
              <div><span class="detail-label">{{ selectedKnowledge.language === 'text' ? '参考实验模板' : '参考实现' }}</span><button @click="copyReference">复制内容</button></div>
              <p class="reference-warning">先独立复现，再用参考实现核对数据流、异常和资源清理。</p>
              <pre><code>{{ selectedKnowledge.reference_code }}</code></pre>
              <p v-if="selectedKnowledge.run_command" class="run-command"><b>运行：</b><code>{{ selectedKnowledge.run_command }}</code></p>
            </section>
            <section v-if="selectedKnowledge.code_explanation?.length"><span class="detail-label">代码为什么这样写</span><ol class="code-explanation"><li v-for="(line, index) in selectedKnowledge.code_explanation" :key="line"><b>{{ index + 1 }}</b><span>{{ line }}</span></li></ol></section>
            <section><span class="detail-label">预期结果</span><ul class="result-list"><li v-for="result in selectedKnowledge.expected_results" :key="result">{{ result }}</li></ul></section>
            <section><span class="detail-label">需要掌握的结果</span><ul class="mastery-list"><li v-for="item in selectedKnowledge.mastery" :key="item">{{ item }}</li></ul></section>
            <section v-if="selectedKnowledge.resources?.length"><span class="detail-label">参考资料</span><div class="resource-list"><a v-for="resource in selectedKnowledge.resources" :key="resource.url" :href="resource.url" target="_blank" rel="noopener noreferrer"><span>{{ resource.title }}</span><b aria-hidden="true">↗</b></a></div></section>
          </div>
          <footer><p v-if="saveError" class="notice error" role="alert">{{ saveError }}，请重试标记。</p><button class="button ghost" @click="askAboutKnowledge">让 AI 辅导这个知识点</button><button class="button secondary" :disabled="markingKnowledge" @click="markKnowledgeComplete">{{ markingKnowledge ? '正在保存…' : progress.knowledge_checks[selectedKnowledgeIndex] ? '已学习' : '完成复现，标记已学习' }}</button></footer>
        </article>
      </dialog>
    </div>
  </AppShell>
</template>
