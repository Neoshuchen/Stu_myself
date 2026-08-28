<script setup>
defineProps({ title: String, copy: String, action: String })
defineEmits(['action'])
</script>

<template>
  <div class="empty-state">
    <span class="empty-orbit">知</span>
    <h2>{{ title }}</h2>
    <p>{{ copy }}</p>
    <button v-if="action" class="button primary" @click="$emit('action')">{{ action }}</button>
  </div>
</template>
