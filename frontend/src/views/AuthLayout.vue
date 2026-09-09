<script setup>
defineProps({ title: String, copy: String })
</script>

<template>
  <main class="auth-page">
    <section class="auth-story">
      <RouterLink class="brand" to="/"><span class="brand-mark">知</span><b>知序</b></RouterLink>
      <div class="story-copy">
        <span class="story-kicker">给自学一条清晰的路径</span>
        <h1>{{ title }}</h1>
        <p>{{ copy }}</p>
        <ol class="story-steps"><li><b>选一条路线</b><span>把长期目标拆成每天的行动</span></li><li><b>做一个实验</b><span>从理解到复现，亲手验证所学</span></li><li><b>留一份证据</b><span>用真实成果，看见自己的进步</span></li></ol>
      </div>
      <div class="story-card">
        <span>今日原则</span>
        <blockquote>真正的进度，不是看过多少，而是能否独立复现。</blockquote>
      </div>
    </section>
    <section class="auth-form-wrap"><div class="auth-form"><RouterLink class="brand auth-mobile-brand" to="/"><span class="brand-mark">知</span><b>知序</b></RouterLink><slot /></div></section>
  </main>
</template>
