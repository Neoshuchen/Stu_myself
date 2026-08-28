<script setup>
defineProps({ title: String, copy: String })
</script>

<template>
  <main class="auth-page">
    <section class="auth-story">
      <RouterLink class="brand" to="/"><span class="brand-mark">知</span><b>知序</b></RouterLink>
      <div class="story-copy">
        <h1>{{ title }}</h1>
        <p>{{ copy }}</p>
      </div>
      <div class="story-card">
        <span>今日原则</span>
        <blockquote>真正的进度，不是看过多少，而是能否独立复现。</blockquote>
      </div>
    </section>
    <section class="auth-form-wrap"><div class="auth-form"><slot /></div></section>
  </main>
</template>
