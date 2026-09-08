<script setup>
import { computed, nextTick, ref } from 'vue'

import { api } from '../api'
import { pastedImages, resizeUploadImage } from '../image'

const ADAPTER_OPTIONS = [
  { id: 'openai_chat_completions', provider: 'openai', name: 'OpenAI 兼容 / Chat Completions', defaultUrl: 'https://api.openai.com/v1' },
  { id: 'openai_responses', provider: 'openai', name: 'OpenAI Responses', defaultUrl: 'https://api.openai.com/v1' },
  { id: 'anthropic_messages', provider: 'anthropic', name: 'Anthropic Messages', defaultUrl: 'https://api.anthropic.com/v1' },
]
const QUICK_PROMPTS = ['解释一个我没理解的概念', '分析报错并给出排查步骤', '根据上传材料出 3 道练习题']

const dialog = ref(null)
const messageList = ref(null)
const fileInput = ref(null)
const catalog = ref(null)
const initialized = ref(false)
const credentials = ref([])
const sessions = ref([])
const activeSession = ref(null)
const messages = ref([])
const loading = ref(false)
let sessionLoadVersion = 0
const sending = ref(false)
const configBusy = ref(false)
const preparingFiles = ref(false)
const error = ref('')
const configNotice = ref('')
const draft = ref('')
const focus = ref(null)
const files = ref([])
const temporaryKey = ref('')
const temporaryKeyEndpoint = ref('')
const configurationName = ref('我的模型配置')
const editingCredentialId = ref(null)
const selectedCredentialId = ref(null)
const configured = ref(false)
const provider = ref(ADAPTER_OPTIONS[0].provider)
const adapter = ref(ADAPTER_OPTIONS[0].id)
const apiUrl = ref(ADAPTER_OPTIONS[0].defaultUrl)
const model = ref('')
const contextRounds = ref(8)
const maxOutputTokens = ref(1024)
const teachingMode = ref('hint')

const attachmentMinutes = computed(() => Math.floor((catalog.value?.attachment_cache_ttl_seconds || 0) / 60))
const activeEndpoint = computed(() => activeSession.value || { provider: provider.value, adapter: adapter.value, api_url: apiUrl.value })
const matchingCredential = computed(() => {
  const credentialId = activeSession.value?.credential || selectedCredentialId.value
  const selected = credentials.value.find((item) => item.id === credentialId)
  if (selected) return sameEndpoint(selected, activeEndpoint.value) ? selected : null
  return credentials.value.find((item) => sameEndpoint(item, activeEndpoint.value)) || null
})
const needsTemporaryKey = computed(() => Boolean(activeEndpoint.value) && !matchingCredential.value)
const temporaryKeyMatchesEndpoint = computed(() => (
  Boolean(temporaryKey.value) && temporaryKeyEndpoint.value === endpointIdentity(activeEndpoint.value)
))
const canSend = computed(() => (
  !sending.value
  && !loading.value
  && !preparingFiles.value
  && (activeSession.value || configured.value)
  && (!needsTemporaryKey.value || temporaryKeyMatchesEndpoint.value)
  && (draft.value.trim() || files.value.length)
))

/** 打开可跨页面使用的学习助手；首次打开时加载配置和全部个人会话。 */
async function open() {
  error.value = ''
  dialog.value?.showModal()
  if (!initialized.value) await loadAssistant()
}

/** 直接打开账号级模型服务页面，供路线生成等全局入口复用。 */
async function openConfiguration() {
  await open()
  if (initialized.value && catalog.value?.enabled) showConfiguration()
}

/** 接收知识点标题和正文，准备新对话草稿；只在用户发送时提交上下文。 */
async function openFocus(context) {
  await open()
  if (sending.value) {
    error.value = '当前问题仍在发送，请完成后再选择知识点。'
    return
  }
  startNewSession()
  focus.value = { title: String(context?.title || '').slice(0, 160), content: String(context?.content || '').slice(0, 4000) }
  if (!draft.value.trim()) draft.value = '请用一个具体例子引导我理解这个知识点，先问我一个问题，再根据回答给提示。'
}

/** 关闭全局抽屉；临时 Key 仅保留到当前登录页面生命周期结束。 */
function close() {
  if (dialog.value?.open) dialog.value.close()
}

async function loadAssistant() {
  const version = sessionLoadVersion
  loading.value = true
  error.value = ''
  configNotice.value = ''
  try {
    const nextCatalog = await api('/ai/providers/')
    catalog.value = nextCatalog
    if (!nextCatalog.enabled) {
      initialized.value = true
      return
    }
    const [savedCredentials, savedSessions] = await Promise.all([api('/ai/credentials/'), api('/ai/chats/')])
    credentials.value = savedCredentials
    sessions.value = savedSessions
    initialized.value = true
    if (savedSessions.length) await loadSession(savedSessions[0].id)
    else if (savedCredentials.length) applyCredential(savedCredentials[0])
    else resetConfigurationForm()
  } catch (err) {
    if (version === sessionLoadVersion) error.value = err.message
  } finally {
    // 初始会话也可能被用户的新选择替代，外层请求不能提前解除后续加载状态。
    if (version === sessionLoadVersion) loading.value = false
  }
}

function sameEndpoint(left, right) {
  return Boolean(left && right)
    && left.provider === right.provider
    && (left.adapter || '') === (right.adapter || '')
    && (left.api_url || '') === (right.api_url || '')
}

function endpointIdentity(endpoint) {
  return endpoint ? `${endpoint.provider}|${endpoint.adapter || ''}|${endpoint.api_url || ''}` : ''
}

function setTemporaryKey(value) {
  temporaryKey.value = value
  temporaryKeyEndpoint.value = value ? endpointIdentity(activeEndpoint.value) : ''
}

function clearTemporaryKey() {
  temporaryKey.value = ''
  temporaryKeyEndpoint.value = ''
}

function adapterName(value) {
  return ADAPTER_OPTIONS.find((item) => item.id === value)?.name || (value || '旧版官方接口')
}

function resetConfigurationForm() {
  const option = ADAPTER_OPTIONS[0]
  configurationName.value = '我的模型配置'
  editingCredentialId.value = null
  selectedCredentialId.value = null
  provider.value = option.provider
  adapter.value = option.id
  apiUrl.value = option.defaultUrl
  model.value = ''
  clearTemporaryKey()
  configured.value = false
}

function selectAdapter(value) {
  const option = ADAPTER_OPTIONS.find((item) => item.id === value)
  if (!option) return
  adapter.value = option.id
  provider.value = option.provider
  apiUrl.value = option.defaultUrl
  model.value = ''
  clearTemporaryKey()
  configNotice.value = ''
}

function applyCredential(credential) {
  configurationName.value = credential.name
  editingCredentialId.value = null
  selectedCredentialId.value = credential.id
  provider.value = credential.provider
  adapter.value = credential.adapter || ''
  apiUrl.value = credential.api_url || ''
  model.value = credential.model || catalog.value?.providers.find((item) => item.id === credential.provider)?.models[0] || ''
  clearTemporaryKey()
  configured.value = true
  configNotice.value = `已使用“${credential.name}” ····${credential.key_last_four}`
}

function configurationPayload() {
  return {
    name: configurationName.value.trim(),
    provider: provider.value,
    adapter: adapter.value,
    api_url: apiUrl.value.trim(),
    model: model.value.trim(),
    api_key: temporaryKey.value.trim(),
  }
}

function useTemporaryConfiguration() {
  editingCredentialId.value = null
  selectedCredentialId.value = null
  temporaryKeyEndpoint.value = endpointIdentity(activeEndpoint.value)
  configured.value = true
  error.value = ''
  configNotice.value = '当前使用临时配置，API Key 不会写入浏览器持久存储。'
}

async function testConfiguration() {
  configBusy.value = true
  error.value = ''
  configNotice.value = ''
  try {
    const result = await api('/ai/credentials/test/', { method: 'POST', body: JSON.stringify(configurationPayload()) })
    configNotice.value = result.detail
  } catch (err) { error.value = err.message } finally { configBusy.value = false }
}

async function saveConfiguration() {
  configBusy.value = true
  error.value = ''
  configNotice.value = ''
  try {
    const payload = configurationPayload()
    if (!payload.api_key) delete payload.api_key
    const editing = editingCredentialId.value
    const saved = await api(editing ? `/ai/credentials/${editing}/` : '/ai/credentials/', {
      method: editing ? 'PATCH' : 'POST',
      body: JSON.stringify(payload),
    })
    credentials.value = editing
      ? credentials.value.map((item) => item.id === saved.id ? saved : item)
      : [saved, ...credentials.value]
    applyCredential(saved)
    window.dispatchEvent(new CustomEvent('ai-credentials-changed', { detail: saved }))
    configNotice.value = '模型配置已保存并与当前账号绑定。'
  } catch (err) { error.value = err.message } finally { configBusy.value = false }
}

async function removeCredential(credential) {
  if (!confirm(`确认删除模型配置“${credential.name}” ····${credential.key_last_four}？`)) return
  configBusy.value = true
  error.value = ''
  try {
    await api(`/ai/credentials/${credential.id}/`, { method: 'DELETE' })
    credentials.value = credentials.value.filter((item) => item.id !== credential.id)
    if (selectedCredentialId.value === credential.id) resetConfigurationForm()
    window.dispatchEvent(new CustomEvent('ai-credentials-changed'))
    configNotice.value = '已删除保存的模型配置；已有对话仍会保留。'
  } catch (err) { error.value = err.message } finally { configBusy.value = false }
}

function editCredential(credential) {
  configurationName.value = credential.name
  editingCredentialId.value = credential.id
  selectedCredentialId.value = credential.id
  provider.value = credential.provider
  adapter.value = credential.adapter || ''
  apiUrl.value = credential.api_url || ''
  model.value = credential.model || ''
  clearTemporaryKey()
  configured.value = false
  error.value = ''
  configNotice.value = '正在修改已保存配置；API Key 留空会继续使用原密钥。'
}

function showConfiguration() {
  if (sending.value) return
  sessionLoadVersion += 1
  loading.value = false
  activeSession.value = null
  messages.value = []
  configured.value = false
  error.value = ''
  configNotice.value = ''
  if (!adapter.value) resetConfigurationForm()
}

async function loadSession(id) {
  if (sending.value) return
  focus.value = null
  if (!id) {
    startNewSession()
    return
  }
  const version = ++sessionLoadVersion
  loading.value = true
  error.value = ''
  try {
    const loaded = await api(`/ai/chats/${id}/`)
    // 只允许最后一次选择更新会话；新对话和配置页也会废止旧请求。
    if (version !== sessionLoadVersion) return
    activeSession.value = loaded
    messages.value = activeSession.value.messages || []
    provider.value = activeSession.value.provider
    adapter.value = activeSession.value.adapter || ''
    apiUrl.value = activeSession.value.api_url || ''
    model.value = activeSession.value.model
    contextRounds.value = activeSession.value.context_rounds
    maxOutputTokens.value = activeSession.value.max_output_tokens
    teachingMode.value = activeSession.value.teaching_mode
    selectedCredentialId.value = activeSession.value.credential
    editingCredentialId.value = null
    configurationName.value = credentials.value.find((item) => item.id === activeSession.value.credential)?.name || '对话模型配置'
    if (!temporaryKeyMatchesEndpoint.value) clearTemporaryKey()
    configured.value = true
    await scrollToLatest()
  } catch (err) {
    if (version === sessionLoadVersion) error.value = err.message
  } finally {
    if (version === sessionLoadVersion) loading.value = false
  }
}

function startNewSession() {
  if (sending.value) return
  sessionLoadVersion += 1
  loading.value = false
  focus.value = null
  if (activeSession.value) {
    selectedCredentialId.value = activeSession.value.credential
    provider.value = activeSession.value.provider
    adapter.value = activeSession.value.adapter || ''
    apiUrl.value = activeSession.value.api_url || ''
    model.value = activeSession.value.model
    configured.value = true
  } else if (!configured.value && credentials.value.length) {
    applyCredential(credentials.value[0])
  }
  activeSession.value = null
  messages.value = []
  error.value = ''
}

async function createSession(initialTitle = draft.value.trim()) {
  const hadMatchingTemporaryKey = temporaryKeyMatchesEndpoint.value
  const created = await api('/ai/chats/', {
    method: 'POST',
    body: JSON.stringify({
      title: (initialTitle || 'AI 学习对话').slice(0, 120),
      credential: matchingCredential.value?.id || null,
      provider: provider.value,
      adapter: adapter.value,
      api_url: apiUrl.value,
      model: model.value,
      context_rounds: contextRounds.value,
      max_output_tokens: maxOutputTokens.value,
      teaching_mode: teachingMode.value,
      include_current_lesson: false,
    }),
  })
  sessions.value.unshift(created)
  activeSession.value = created
  apiUrl.value = created.api_url || apiUrl.value
  // 后端会把 Base URL 规范化为完整端点，临时 Key 必须随同迁移到同一安全身份。
  if (hadMatchingTemporaryKey && temporaryKey.value) temporaryKeyEndpoint.value = endpointIdentity(created)
  return created
}

async function removeSession() {
  if (!activeSession.value || !confirm(`确认删除对话“${activeSession.value.title}”？`)) return
  const deleted = activeSession.value
  try {
    await api(`/ai/chats/${deleted.id}/`, { method: 'DELETE' })
    sessions.value = sessions.value.filter((item) => item.id !== deleted.id)
    startNewSession()
  } catch (err) { error.value = err.message }
}

/** 校验并准备新附件；文件选择替换现有附件，剪贴板图片追加到现有附件。 */
async function prepareSelectedFiles(selected, replace = false) {
  const maxFiles = catalog.value?.attachment_max_files || 1
  const maxBytes = catalog.value?.attachment_max_bytes || 0
  const existing = replace ? [] : files.value
  error.value = ''
  if (existing.length + selected.length > maxFiles) {
    error.value = `每次最多上传 ${maxFiles} 个附件。`
    return false
  }
  preparingFiles.value = true
  try {
    // 图片在浏览器内先缩放；文本、源码和 PDF 仍由服务端按白名单读取。
    const prepared = await Promise.all(selected.map(async (file) => {
      if (file.type.startsWith('image/')) return resizeUploadImage(file, maxBytes)
      if (file.size > maxBytes) throw new Error(`附件 ${file.name} 超过 ${Math.floor(maxBytes / 1024 / 1024)}MB。`)
      return file
    }))
    files.value = [...existing, ...prepared]
    return true
  } catch (err) {
    error.value = err.message || '无法读取附件，请更换文件后重试。'
    return false
  } finally {
    preparingFiles.value = false
  }
}

/** 处理文件选择器内容，并允许用户再次选择同名文件。 */
async function filesChanged(event) {
  await prepareSelectedFiles([...event.target.files], true)
  event.target.value = ''
}

/** 将剪贴板中的 PNG、JPEG 或 WebP 图片作为附件追加，不影响普通文字粘贴。 */
async function imagesPasted(event) {
  const images = pastedImages(event)
  if (!images.length) return
  event.preventDefault()
  await prepareSelectedFiles(images)
}

/** 移除一个尚未发送的附件；发送中的 FormData 不允许再被界面修改。 */
function removeSelectedFile(index) {
  if (sending.value || preparingFiles.value) return
  files.value = files.value.filter((_file, fileIndex) => fileIndex !== index)
  error.value = ''
}

/** 使用 Enter 发送、Shift+Enter 换行，并避开输入法正在组合文字的阶段。 */
function composerKeydown(event) {
  if (event.key !== 'Enter' || event.shiftKey || event.isComposing || !canSend.value) return
  event.preventDefault()
  sendMessage()
}

async function sendMessage() {
  if (!canSend.value) return
  const submittedContent = draft.value.trim()
  const submittedFiles = [...files.value]
  const submittedFocus = focus.value ? { ...focus.value } : null
  const optimisticId = `pending-${Date.now()}`
  const optimisticMessage = {
    id: optimisticId,
    role: 'user',
    content: submittedContent,
    attachments: submittedFiles.map((file) => ({
      name: file.name,
      kind: file.type.startsWith('image/') ? 'image' : 'text',
    })),
  }
  sending.value = true
  error.value = ''
  messages.value.push(optimisticMessage)
  draft.value = ''
  files.value = []
  focus.value = null
  if (fileInput.value) fileInput.value.value = ''
  await scrollToLatest()
  try {
    const session = activeSession.value || await createSession(submittedContent)
    const form = new FormData()
    form.append('content', submittedContent)
    if (submittedFocus) {
      form.append('focus_title', submittedFocus.title)
      form.append('focus_content', submittedFocus.content)
    }
    if (temporaryKeyMatchesEndpoint.value) form.append('api_key', temporaryKey.value)
    submittedFiles.forEach((file) => form.append('attachments', file))
    const result = await api(`/ai/chats/${session.id}/messages/`, { method: 'POST', body: form })
    const optimisticIndex = messages.value.findIndex((message) => message.id === optimisticId)
    // 等待供应商期间用户可能切换会话；只替换仍属于当前视图的临时消息。
    if (optimisticIndex >= 0) {
      messages.value.splice(optimisticIndex, 1, result.user_message, result.assistant_message)
    }
    const listed = sessions.value.find((item) => item.id === session.id)
    if (listed) listed.message_count = (listed.message_count || 0) + 2
    await scrollToLatest()
  } catch (err) {
    messages.value = messages.value.filter((message) => message.id !== optimisticId)
    draft.value = submittedContent
    files.value = submittedFiles
    focus.value = submittedFocus
    error.value = err.message
  } finally {
    sending.value = false
  }
}

async function scrollToLatest() {
  await nextTick()
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
}

defineExpose({ open, openConfiguration, openFocus })
</script>

<template>
  <dialog ref="dialog" class="ai-tutor-dialog" aria-labelledby="ai-tutor-title" @click.self="close">
    <article :class="['ai-tutor-drawer', { standalone: !initialized || !catalog?.enabled }]">
      <aside v-if="initialized && catalog?.enabled" class="ai-tutor-sidebar">
        <div class="ai-brand"><span>AI</span><div><b>学习助手</b><small>你的全局学习空间</small></div></div>
        <button class="ai-new-chat" type="button" @click="startNewSession"><span>＋</span> 新对话</button>
        <nav class="ai-session-nav" aria-label="历史对话">
          <small>最近对话</small>
          <button v-for="session in sessions" :key="session.id" type="button" :aria-current="activeSession?.id === session.id ? 'page' : undefined" @click="loadSession(session.id)">
            <span>{{ session.title }}</span><small>{{ session.message_count }} 条消息</small>
          </button>
          <p v-if="!sessions.length">还没有历史对话</p>
        </nav>
        <footer>
          <button type="button" @click="showConfiguration"><span>模型服务</span><small>{{ credentials.length ? `已保存 ${credentials.length} 个配置` : '尚未配置' }}</small></button>
        </footer>
      </aside>

      <main class="ai-tutor-main">
        <header class="ai-tutor-topbar">
          <div>
            <span class="eyebrow">GLOBAL AI STUDY TUTOR</span>
            <h2 id="ai-tutor-title">{{ activeSession?.title || (!configured && initialized ? '模型服务' : '新对话') }}</h2>
            <p v-if="activeSession">{{ activeSession.model }} · {{ activeSession.context_rounds }} 轮上下文</p>
            <p v-else>随时提问，支持图片、PDF、文本和源码</p>
          </div>
          <div class="ai-topbar-actions">
            <select v-if="catalog?.enabled" class="ai-mobile-session-select" aria-label="选择历史对话" :value="activeSession?.id || ''" @change="loadSession($event.target.value)"><option value="">新对话</option><option v-for="session in sessions" :key="session.id" :value="session.id">{{ session.title }}</option></select>
            <button v-if="initialized && catalog?.enabled" type="button" aria-label="管理模型服务" title="管理模型服务" @click="showConfiguration">⚙</button>
            <button v-if="activeSession" class="danger-text" type="button" aria-label="删除当前对话" title="删除当前对话" @click="removeSession">⌫</button>
            <button type="button" aria-label="关闭学习助手" title="关闭" @click="close">×</button>
          </div>
        </header>

        <div v-if="loading && !initialized" class="ai-tutor-loading">正在加载学习助手…</div>
        <div v-else-if="!initialized" class="ai-tutor-empty"><b>暂时无法加载学习助手</b><p>{{ error || '无法连接本站 AI 接口，请确认后端服务和登录状态后重试。' }}</p><button class="button ghost" type="button" @click="loadAssistant">重试</button></div>
        <div v-else-if="!catalog?.enabled" class="ai-tutor-empty"><b>AI 学习助手暂未启用</b><p>请先由站点管理员开启 AI 功能；其他学习功能不受影响。</p></div>

        <form v-else-if="!activeSession && !configured" class="ai-connection-form" @submit.prevent="useTemporaryConfiguration">
          <div class="ai-config-intro"><span class="eyebrow">账号级配置</span><h3>连接模型服务</h3><p>配置使用独立主密钥加密后与当前账号绑定，重新登录后可继续使用。</p></div>
          <section v-if="credentials.length" class="ai-config-section">
            <header><h4>已保存的服务</h4><small>可保存多个供应商并随时切换</small></header>
            <div class="ai-saved-credentials">
              <div v-for="item in credentials" :key="item.id"><span><b>{{ item.name }}</b><small>{{ item.model || '默认模型' }} · {{ adapterName(item.adapter) }} · ····{{ item.key_last_four }}</small></span><div class="button-row"><button class="text-action" type="button" @click="applyCredential(item)">使用</button><button class="text-action" type="button" @click="editCredential(item)">编辑</button><button class="text-action danger-text" type="button" :disabled="configBusy" @click="removeCredential(item)">删除</button></div></div>
            </div>
          </section>
          <section class="ai-config-section ai-setup-card">
            <header><h4>{{ editingCredentialId ? '修改模型服务' : '添加模型服务' }}</h4><small>兼容 OpenCode / AI SDK 的 Base URL 配置方式</small></header>
            <div class="ai-connection-grid">
              <label>配置名称<input v-model.trim="configurationName" required maxlength="80" placeholder="例如：DeepSeek 学习模型" /></label>
              <label>接口协议<select :value="adapter" required @change="selectAdapter($event.target.value)"><option v-for="item in ADAPTER_OPTIONS" :key="item.id" :value="item.id">{{ item.name }}</option></select></label>
              <label>模型名称<input v-model.trim="model" required maxlength="100" placeholder="例如：deepseek-v4-pro" /></label>
              <label class="wide">API Base URL<input v-model.trim="apiUrl" type="url" required maxlength="500" placeholder="https://provider.example/v1" /><small>填写到版本路径即可，系统会按协议补全；也兼容完整请求地址。</small></label>
              <label class="wide">API Key<input :value="temporaryKey" type="password" autocomplete="off" :required="!editingCredentialId" maxlength="512" :placeholder="editingCredentialId ? '留空则继续使用原密钥' : '只在提交时发送，不写入浏览器存储'" @input="setTemporaryKey($event.target.value.trim())" /></label>
            </div>
          </section>
          <p class="field-hint">仅接受解析到公网地址的 HTTPS 服务，禁止本机、内网、保留地址和重定向。测试连接会产生一次极小的模型请求。</p>
          <p v-if="!catalog.credential_storage_available" class="form-error">服务端未配置独立凭据加密密钥，当前只能临时使用；切勿把 Key 存入浏览器。</p>
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
          <p v-if="configNotice" class="notice success">{{ configNotice }}</p>
          <div class="ai-config-actions"><button class="button ghost" type="button" :disabled="configBusy || !temporaryKey || !model || !apiUrl" @click="testConfiguration">测试连接</button><button class="button secondary" type="submit" :disabled="configBusy || !temporaryKey">仅本次使用</button><button class="button primary" type="button" :disabled="configBusy || !catalog.credential_storage_available || (!editingCredentialId && !temporaryKey) || !configurationName || !model || !apiUrl" @click="saveConfiguration">{{ editingCredentialId ? '保存修改并使用' : '验证、保存并使用' }}</button></div>
        </form>

        <section v-else class="ai-chat-view">
          <div class="ai-model-bar">
            <span><i></i><b>{{ matchingCredential?.name || '临时模型配置' }}</b><small>{{ model }}</small></span>
            <details v-if="!activeSession" class="ai-chat-options">
              <summary>对话设置</summary>
              <div>
                <label>上下文<select v-model.number="contextRounds"><option :value="4">4 轮</option><option :value="8">8 轮</option><option :value="12">12 轮</option></select></label>
                <label>讲解方式<select v-model="teachingMode"><option value="hint">提示优先</option><option value="explain">详细讲解</option><option value="example">举例对比</option><option value="debug">报错分析</option><option value="quiz">出题检验</option></select></label>
                <label>回复长度<select v-model.number="maxOutputTokens"><option :value="512">简短</option><option :value="1024">标准</option><option :value="2048">详细</option><option :value="4096">最长</option></select></label>
              </div>
            </details>
            <button v-else class="text-action" type="button" @click="startNewSession">基于此配置新建对话</button>
          </div>

          <label v-if="needsTemporaryKey" class="ai-key-field"><span>此对话没有匹配的已保存密钥，请输入本次 API Key</span><input :value="temporaryKey" type="password" autocomplete="off" placeholder="仅用于当前页面，不会持久化" @input="setTemporaryKey($event.target.value.trim())" /></label>

          <div ref="messageList" class="ai-message-list" aria-live="polite">
            <div v-if="!messages.length" class="ai-chat-welcome">
              <span>AI</span><h3>今天想弄懂什么？</h3><p>给出背景、预期和实际结果，回答会更准确。</p>
              <div><button v-for="prompt in QUICK_PROMPTS" :key="prompt" type="button" @click="draft = prompt">{{ prompt }}</button></div>
            </div>
            <article v-for="message in messages" :key="message.id" :class="['ai-message', message.role]">
              <small>{{ message.role === 'assistant' ? '学习助手' : '你' }}<template v-if="message.role === 'assistant' && (message.input_tokens || message.output_tokens)"> · 输入 {{ message.input_tokens }} / 输出 {{ message.output_tokens }} tokens</template></small>
              <p>{{ message.content || '（仅上传附件）' }}</p>
              <div v-if="message.attachments?.length" class="ai-attachment-list"><span v-for="item in message.attachments" :key="`${message.id}-${item.name}`">{{ item.kind === 'image' ? '图片' : '文件' }} · {{ item.name }}{{ item.truncated ? '（已截断）' : '' }}</span></div>
            </article>
            <div v-if="sending" class="ai-message assistant pending">学习助手正在分析…</div>
          </div>

          <form class="ai-composer" @submit.prevent="sendMessage">
            <details v-if="focus" class="ai-focus-preview" open>
              <summary>下一条消息将附带此知识点</summary>
              <label>知识点标题<input v-model="focus.title" maxlength="160" /></label>
              <label>将发送的正文<textarea v-model="focus.content" rows="4" maxlength="4000"></textarea></label>
              <button type="button" class="text-action" @click="focus = null">移除知识点上下文</button>
            </details>
            <div class="ai-composer-box">
              <textarea v-model="draft" rows="3" :maxlength="6000" :disabled="sending" placeholder="输入问题，可直接粘贴图片；Enter 发送，Shift+Enter 换行" @paste="imagesPasted" @keydown="composerKeydown"></textarea>
              <div v-if="files.length" class="ai-selected-attachments" aria-label="待发送附件">
                <span v-for="(file, index) in files" :key="`${file.name}-${file.lastModified}-${index}`">
                  <span :title="file.name">{{ file.name }}</span>
                  <button type="button" :disabled="sending || preparingFiles" :aria-label="`移除附件 ${file.name}`" title="移除附件" @click="removeSelectedFile(index)">×</button>
                </span>
              </div>
              <div class="ai-composer-actions">
                <label class="file-input" :title="files.length ? '重新选择并替换全部附件' : '添加图片或文件'"><input ref="fileInput" type="file" multiple :disabled="sending || preparingFiles" accept="image/png,image/jpeg,image/webp,.pdf,.txt,.md,.log,.csv,.json,.yaml,.yml,.xml,.py,.js,.ts,.vue,.html,.css,.sql,.sh,.ps1,.java,.kt,.swift,.c,.h,.cpp,.go,.rs" @change="filesChanged" /><span>{{ preparingFiles ? '处理中…' : files.length ? '↻ 替换附件' : '＋ 添加附件' }}</span></label>
                <small v-if="files.length" class="ai-attachment-count">{{ files.length }} 个附件</small>
                <button class="ai-send-button" :disabled="!canSend" aria-label="发送问题">{{ sending ? '分析中' : '发送' }}</button>
              </div>
            </div>
            <p v-if="error" class="form-error" role="alert">{{ error }}</p>
            <small class="ai-privacy-note">内容会发送到你配置的第三方模型；附件在 Redis 中最长保留约 {{ attachmentMinutes }} 分钟，请勿上传秘密。</small>
          </form>
        </section>
      </main>
    </article>
  </dialog>
</template>
