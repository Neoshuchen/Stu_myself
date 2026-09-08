<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { auth } from './auth'
import AiTutorDrawer from './components/AiTutorDrawer.vue'

const aiTutor = ref(null)

function openAiConfiguration() {
  aiTutor.value?.openConfiguration()
}

/** 将学习页选择的知识点转交全局助手，等待用户编辑并发送。 */
function openAiFocus(event) {
  aiTutor.value?.openFocus(event.detail)
}

onMounted(() => window.addEventListener('open-ai-configuration', openAiConfiguration))
onBeforeUnmount(() => window.removeEventListener('open-ai-configuration', openAiConfiguration))
onMounted(() => window.addEventListener('open-ai-focus', openAiFocus))
onBeforeUnmount(() => window.removeEventListener('open-ai-focus', openAiFocus))
</script>

<template>
  <router-view />
  <template v-if="auth.loggedIn">
    <button class="global-ai-launcher" aria-label="打开全局 AI 学习助手" @click="aiTutor?.open()"><span>AI</span>学习助手</button>
    <AiTutorDrawer ref="aiTutor" />
  </template>
</template>
