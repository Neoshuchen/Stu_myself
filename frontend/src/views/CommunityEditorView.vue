<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const route = useRoute()
const router = useRouter()
const form = ref({ post_type: 'share', title: '', content: '', plan: null, plan_day: null })
const plans = ref([])
const selectedPlan = ref(null)
const error = ref('')
const busy = ref(false)
const imageFiles = ref([])
const existingImages = ref([])
const removedImageIds = ref([])
const editing = computed(() => Boolean(route.params.id))
const fixedPlan = computed(() => Boolean(route.params.slug))
const loading = ref(editing.value || fixedPlan.value)
const availableDays = computed(() => selectedPlan.value?.days || [])

onMounted(async () => {
  try {
    // 展柜草稿只经过浏览器导航状态；点击发布前不会写入社区。
    const showcaseDraft = window.history.state?.showcaseDraft
    if (!editing.value && !fixedPlan.value && showcaseDraft) {
      form.value.title = String(showcaseDraft.title || '').slice(0, 160)
      form.value.content = String(showcaseDraft.content || '')
      form.value.post_type = 'project'
    }
    plans.value = await api('/plans/')
    if (fixedPlan.value) {
      selectedPlan.value = await api(`/plans/${route.params.slug}/`)
      form.value.plan = selectedPlan.value.id
    } else if (editing.value) {
      const post = await api(`/community/posts/${route.params.id}/`)
      if (!post.owned) return router.replace(`/community/posts/${post.id}`)
      form.value = { post_type: post.post_type, title: post.title, content: post.content, plan: post.plan, plan_day: post.plan_day }
      existingImages.value = post.images || []
      if (post.plan_slug) selectedPlan.value = await api(`/plans/${post.plan_slug}/`)
    }
    const day = Number(route.query.day)
    if (day && selectedPlan.value) form.value.plan_day = selectedPlan.value.days.find((item) => item.day_number === day)?.id || null
    if (route.query.type) form.value.post_type = route.query.type
    if (route.query.content) form.value.content = String(route.query.content)
  } catch (err) { error.value = err.message } finally { loading.value = false }
})

async function planChanged() {
  form.value.plan_day = null
  selectedPlan.value = form.value.plan ? await api(`/plans/${plans.value.find((item) => item.id === form.value.plan).slug}/`) : null
}

function imagesChanged(event) {
  const selected = [...event.target.files]
  const retained = existingImages.value.length - removedImageIds.value.length
  if (retained + selected.length > 4) {
    error.value = '每篇帖子最多上传4张图片。'
    event.target.value = ''
    return
  }
  imageFiles.value = selected
}

function removeExistingImage(id) {
  if (!removedImageIds.value.includes(id)) removedImageIds.value.push(id)
}

async function submit() {
  busy.value = true
  error.value = ''
  try {
    const payload = new FormData()
    payload.append('post_type', form.value.post_type)
    payload.append('title', form.value.title)
    payload.append('content', form.value.content)
    payload.append('plan', form.value.plan ?? '')
    payload.append('plan_day', form.value.plan_day ?? '')
    imageFiles.value.forEach((file) => payload.append('image_files', file))
    removedImageIds.value.forEach((id) => payload.append('remove_image_ids', id))
    const post = await api(editing.value ? `/community/posts/${route.params.id}/` : '/community/posts/', {
      method: editing.value ? 'PATCH' : 'POST', body: payload,
    })
    router.push(`/community/posts/${post.id}`)
  } catch (err) { error.value = err.message } finally { busy.value = false }
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="loading" />
    <div v-else class="page-enter community-editor">
      <header class="page-heading"><div><span class="eyebrow">SHARE WHAT YOU LEARNED</span><h1>{{ editing ? '继续完善这篇分享' : '把今天学到的说清楚' }}</h1><p>具体的上下文、尝试和结果，比漂亮的结论更有帮助。</p></div></header>
      <p v-if="error" class="notice error">{{ error }}</p>
      <form class="panel community-form" @submit.prevent="submit">
        <div class="editor-fields">
          <label>内容类型<select v-model="form.post_type"><option value="share">技术分享</option><option value="question">问题求助</option><option value="check_in">学习打卡</option><option value="project">项目展示</option></select></label>
          <label v-if="!fixedPlan">发布位置<select v-model="form.plan" @change="planChanged"><option :value="null">全站技术社区</option><option v-for="plan in plans.filter((item) => item.enrolled)" :key="plan.id" :value="plan.id">{{ plan.title }}学习小组</option></select></label>
          <label v-else>发布位置<input :value="`${selectedPlan?.title || ''}学习小组`" disabled /></label>
          <label v-if="selectedPlan">关联学习日<select v-model="form.plan_day"><option :value="null">不关联具体学习日</option><option v-for="day in availableDays" :key="day.id" :value="day.id">Day {{ day.day_number }} · {{ day.title }}</option></select></label>
          <label class="full">标题<input v-model.trim="form.title" required maxlength="160" placeholder="一句话说清楚主题" /></label>
          <label class="full">正文<textarea v-model.trim="form.content" required rows="15" placeholder="背景是什么？你尝试了什么？结果与结论是什么？"></textarea></label>
          <label class="full">配图（可选，最多4张）<input type="file" accept="image/jpeg,image/png,image/webp" multiple @change="imagesChanged" /><small>图片会自动压缩并清除 EXIF/GPS 等拍摄信息。</small></label>
          <div v-if="existingImages.length || imageFiles.length" class="image-edit-grid full">
            <figure v-for="image in existingImages" v-show="!removedImageIds.includes(image.id)" :key="image.id"><img :src="image.url" :alt="image.alt_text || '帖子配图'" /><button type="button" @click="removeExistingImage(image.id)">移除</button></figure>
            <figure v-for="file in imageFiles" :key="`${file.name}-${file.lastModified}`" class="pending-image"><span>{{ file.name }}</span><small>保存后生成预览</small></figure>
          </div>
        </div>
        <footer class="editor-actions"><span>内容会立即发布，请确保不包含密码、Token 等隐私信息。</span><div class="button-row"><button type="button" class="button ghost" @click="router.back()">取消</button><button class="button primary" :disabled="busy">{{ busy ? '正在发布…' : editing ? '保存修改' : '发布分享' }}</button></div></footer>
      </form>
    </div>
  </AppShell>
</template>
