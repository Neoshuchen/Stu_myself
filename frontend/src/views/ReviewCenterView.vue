<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import { api } from '../api'
import AppShell from '../components/AppShell.vue'
import LoadingState from '../components/LoadingState.vue'

const data = ref(null)
const error = ref('')
const submitting = ref(null)
const notes = reactive({})
const answers = reactive({})
const levelPercent = computed(() => {
  const growth = data.value?.growth
  return growth ? Math.round(growth.level_xp / growth.next_level_xp * 100) : 0
})

onMounted(load)

async function load() {
  error.value = ''
  try { data.value = await api('/reviews/') } catch (err) { error.value = err.message }
}

async function submitReview(item, rating) {
  submitting.value = item.progress_id
  error.value = ''
  try {
    data.value = await api('/reviews/', {
      method: 'POST',
      body: JSON.stringify({
        progress: item.progress_id, rating, note: notes[item.progress_id] || '',
        ...(item.quiz ? { answers: answers[item.progress_id] || {}, quiz_token: item.quiz.token } : {}),
      }),
    })
    delete notes[item.progress_id]
    delete answers[item.progress_id]
    window.dispatchEvent(new Event('notifications-changed'))
  } catch (err) { error.value = err.message }
  finally { submitting.value = null }
}

function formatDate(value) {
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

/** 保存本学习日的选择，使用数值选项编号交给服务端判分。 */
function selectAnswer(progressId, questionId, index) {
  answers[progressId] ||= {}
  answers[progressId][questionId] = index
}

/** 检查该学习日是否已选择全部客观题，手工自评始终可提交。 */
function quizComplete(item) {
  return item.quiz?.questions.every(question => Number.isInteger(answers[item.progress_id]?.[question.id]))
}
</script>

<template>
  <AppShell>
    <LoadingState v-if="!data && !error" />
    <div v-else class="page-enter review-page">
      <header class="page-heading compact">
        <div><span class="eyebrow">RECALL STUDIO</span><h1>复习不是重读，是再次想起来</h1><p>系统依据闭卷掌握度、知识缺口和历次结果安排间隔；完成一次有效回忆，可获得 30 XP。</p></div>
      </header>
      <p v-if="error" class="notice error">{{ error }}</p>

      <template v-if="data">
        <section class="growth-hero">
          <div class="level-orbit"><span>LEVEL</span><strong>{{ data.growth.level }}</strong></div>
          <div class="growth-copy"><span class="eyebrow">LEARNING GROWTH</span><h2>{{ data.growth.xp }} XP</h2><p>距离下一级还需 {{ data.growth.next_level_xp - data.growth.level_xp }} XP</p><div class="growth-meter"><i :style="{ width: `${levelPercent}%` }"></i></div></div>
          <div class="growth-stats"><span><strong>{{ data.reviews.due_count }}</strong>今日待复习</span><span><strong>{{ data.growth.completed_bosses }}</strong>Boss 已攻克</span><span><strong>{{ data.growth.badges.filter(item => item.unlocked).length }}</strong>徽章已解锁</span></div>
        </section>

        <section class="badge-section panel">
          <div class="section-title"><div><span class="eyebrow">BADGES</span><h2>学习徽章</h2></div><p>所有徽章都由真实学习记录自动判定</p></div>
          <div class="badge-grid"><article v-for="badge in data.growth.badges" :key="badge.key" :class="{ unlocked: badge.unlocked }"><span>{{ badge.unlocked ? '✓' : badge.progress + '/' + badge.target }}</span><div><b>{{ badge.name }}</b><p>{{ badge.description }}</p></div></article></div>
        </section>

        <section class="review-section">
          <div class="section-title"><div><span class="eyebrow">DUE NOW</span><h2>现在最值得复习</h2></div><p>{{ data.reviews.due_count ? `按优先级整理了 ${data.reviews.due_count} 项` : '当前没有到期项目' }}</p></div>
          <section v-if="data.attempt?.quiz_results?.length" class="panel quiz-feedback" aria-live="polite">
            <h3>本次答对 {{ data.attempt.quiz_results.filter(item => item.correct).length }}/{{ data.attempt.quiz_results.length }} 题 · {{ data.attempt.rating_label }}</h3>
            <p>下次复习：{{ formatDate(data.attempt.next_review_at) }}</p>
            <article v-for="result in data.attempt.quiz_results" :key="result.id"><b>{{ result.correct ? '✓' : '待巩固' }} {{ result.prompt }}</b><p>你的选择：{{ result.selected }} · 正确答案：{{ result.expected }}</p><p>{{ result.explanation }}</p></article>
          </section>
          <div v-if="data.reviews.due.length" class="review-list">
            <article v-for="item in data.reviews.due" :key="item.progress_id" class="review-card panel">
              <header><div><span>{{ item.plan_title }} · Day {{ item.day_number }}</span><h3>{{ item.day_title }}</h3></div><b>{{ item.reason }}</b></header>
              <div class="recall-prompt"><small>{{ item.quiz ? '闭卷三问 · 提交后查看答案与解析' : '请先闭卷回答' }}</small><p>不用查看原文，写出你对“{{ item.core_knowledge }}”的理解、关键步骤或边界条件。</p></div>
              <div v-if="item.quiz" class="recall-quiz">
                <fieldset v-for="(question, questionIndex) in item.quiz.questions" :key="question.id" :disabled="submitting !== null">
                  <legend>{{ questionIndex + 1 }}. {{ question.prompt }}</legend>
                  <label v-for="(option, index) in question.options" :key="index"><input type="radio" :name="`${item.progress_id}-${question.id}`" :checked="answers[item.progress_id]?.[question.id] === index" @change="selectAnswer(item.progress_id, question.id, index)" />{{ option }}</label>
                </fieldset>
              </div>
              <textarea v-model="notes[item.progress_id]" rows="4" maxlength="4000" placeholder="在这里写下闭卷回忆，可留空后口头复现……"></textarea>
              <footer><span>已复习 {{ item.review_count }} 次<span v-if="item.recall_score !== null"> · 原闭卷掌握度 {{ item.recall_score }}%</span><span v-if="item.open_gaps"> · {{ item.open_gaps }} 个开放缺口</span></span><button v-if="item.quiz" class="button primary" :disabled="submitting !== null || !quizComplete(item)" @click="submitReview(item)">提交答案并查看解析</button><div v-else class="review-rating"><button class="button ghost" :disabled="submitting !== null" @click="submitReview(item, 'forgot')">需要重学</button><button class="button secondary" :disabled="submitting !== null" @click="submitReview(item, 'unsure')">基本想起</button><button class="button primary" :disabled="submitting !== null" @click="submitReview(item, 'mastered')">熟练掌握</button></div></footer>
            </article>
          </div>
          <div v-else class="review-empty"><span>✓</span><h3>记忆队列已经清空</h3><p>新的复习项目会按学习结果自动出现，不需要手工安排。</p></div>
        </section>

        <section v-if="data.reviews.upcoming.length" class="panel upcoming-reviews">
          <div class="section-title"><div><span class="eyebrow">UPCOMING</span><h2>接下来会遇到</h2></div></div>
          <article v-for="item in data.reviews.upcoming" :key="item.progress_id"><span>Day {{ item.day_number }}</span><div><b>{{ item.day_title }}</b><p>{{ item.plan_title }} · {{ item.reason }}</p><details v-if="item.latest_results?.length"><summary>上次作答与解析</summary><p v-for="result in item.latest_results" :key="result.id">{{ result.prompt }}<br />你的选择：{{ result.selected }} · 正确答案：{{ result.expected }}<br />{{ result.explanation }}</p></details></div><time>{{ formatDate(item.due_at) }}</time></article>
        </section>
      </template>
    </div>
  </AppShell>
</template>
