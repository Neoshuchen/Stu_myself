<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

import { auth } from './auth'
import AiTutorDrawer from './components/AiTutorDrawer.vue'

const aiTutor = ref(null)

function openAiConfiguration() {
  aiTutor.value?.openConfiguration()
}

onMounted(() => window.addEventListener('open-ai-configuration', openAiConfiguration))
onBeforeUnmount(() => window.removeEventListener('open-ai-configuration', openAiConfiguration))
</script>

<template>
  <router-view />
  <template v-if="auth.loggedIn">
    <button class="global-ai-launcher" aria-label="打开全局 AI 学习助手" @click="aiTutor?.open()"><span>AI</span>学习助手</button>
    <AiTutorDrawer ref="aiTutor" />
  </template>
</template>
