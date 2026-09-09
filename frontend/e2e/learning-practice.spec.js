import { expect, test } from '@playwright/test'

/** 为交互回归隔离 API，不调用真实账号、供应商或发布接口，返回可观察的写入记录。 */
async function preparePage(page, userId = 1, challenges = []) {
  const evidence = { id: userId, title: '变量实验', kind: 'test', content: '私人实验结果', created_at: '2026-09-05T00:00:00Z', is_featured: false }
  const progress = {
    id: 1, enrollment: 1, status: 'in_progress', knowledge_checks: [false], acceptance_checks: [false],
    resume_note: '', reflection: '私人复盘', recall_score: 50, evidence: [evidence], gaps: [],
    day: {
      id: 2, day_number: 2, plan_slug: 'python-foundation-60d', title: '变量与对象', phase: '基础', week_number: 1,
      week_title: 'Python 基础', estimated_minutes: 120, hands_on_task: '复现变量绑定', core_knowledge: '变量绑定',
      acceptance_criteria: ['原列表保持不变'], commands: [], community_supplements: [], content: {},
      knowledge_details: [{ name: '变量绑定', summary: '理解共享对象', basic: '赋值让名字指向对象', mechanism: '修改对象会影响别名', implementation_requirement: '画出两个变量的指向', tools: [], pitfalls: [], mastery: [], expected_results: [] }],
      lab: { id: 'shared-list', title: '案件一：被悄悄改写的原始清单', brief: '定位共享对象', starter: 'result = items\n', checks: 'assert original == [1]\n', hint: '区分绑定与复制', solution: '复制外层列表' },
    },
  }
  const writes = []
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  const credential = { id: 1, name: '测试模型', provider: 'openai', adapter: 'openai_chat_completions', api_url: 'https://provider.example/v1/chat/completions', model: 'test-model', key_last_four: 'test' }
  const questions = [1, 2, 3].map(i => ({ id: `question-${i}`, prompt: `闭卷问题 ${i}`, options: ['选项 A', '选项 B'] }))
  const reviewItem = { progress_id: 1, plan_title: 'Python 基础', day_number: 2, day_title: '变量与对象', core_knowledge: '变量绑定', review_count: 0, recall_score: 50, open_gaps: 0, reason: '到期复习', quiz: { token: 'test-token', questions } }
  const growth = { level: 1, xp: 100, level_xp: 100, next_level_xp: 500, completed_bosses: 0, badges: [] }
  const group = { id: 1, name: '学习小队', invite_code: 'TEAM01', member_count: 2 }
  await page.route('**/api/**', async route => {
    const request = route.request()
    const path = new URL(request.url()).pathname.replace('/api', '')
    const method = request.method()
    if (method !== 'GET') writes.push({ path, body: request.postData() || '' })
    let payload
    if (path === '/auth/csrf/') payload = {}
    else if (path === '/auth/refresh/') payload = { access: 'browser-test-token' }
    else if (path === '/auth/me/') payload = { id: userId, name: `学习者${userId}`, username: `browser-test-${userId}`, is_staff: false }
    else if (path === '/notifications/unread-count/') payload = { count: 0 }
    else if (path === '/dashboard/') payload = { enrollment: null, enrollments: [] }
    else if (path === '/plans/') payload = []
    else if (path === '/enrollments/1/day/' || path === '/progress/1/start/') payload = progress
    else if (path === '/gaps/') {
      payload = { id: 1, ...request.postDataJSON(), status: 'open' }
      progress.gaps.unshift(payload)
    }
    else if (path === '/progress/1/') {
      if (method === 'PATCH') Object.assign(progress, request.postDataJSON())
      payload = progress
    } else if (path === '/evidence/1/feature/') {
      evidence.is_featured = request.postDataJSON().is_featured
      payload = evidence
    } else if (path === '/insights/') payload = {
      summary: { plans: 1, completed_days: 0, knowledge_learned: 0, open_gaps: 0 }, plans: [], repeated_gaps: [],
      showcase: evidence.is_featured ? [{ ...evidence, plan_title: 'Python 基础', day_number: 2, reflection: progress.reflection }] : [],
    }
    else if (path === '/ai/providers/') payload = { enabled: true, credential_storage_available: true, providers: [{ id: 'openai', models: ['test-model'], supports_images: true }], attachment_max_files: 1, attachment_max_bytes: 4194304 }
    else if (path === '/ai/credentials/') payload = [credential]
    else if (path === '/ai/chats/') payload = method === 'GET' ? [] : { ...credential, id: 1, credential: 1, ...request.postDataJSON() }
    else if (path === '/ai/chats/1/messages/') payload = { user_message: { id: 1, role: 'user', content: '请给提示' }, assistant_message: { id: 2, role: 'assistant', content: '先画出变量指向。' } }
    else if (path === '/reviews/') {
      payload = { growth, reviews: { due_count: 1, due: [reviewItem], upcoming: [] } }
      if (method === 'POST') payload = { growth, reviews: { due_count: 0, due: [], upcoming: [] }, attempt: {
        rating_label: '熟练掌握', next_review_at: '2026-09-12T00:00:00Z',
        quiz_results: questions.map(q => ({ id: q.id, prompt: q.prompt, selected: '选项 B', expected: '选项 B', correct: true, explanation: '提交后的解释' })),
      } }
    } else if (path === '/study-groups/') payload = [group]
    else if (path === '/study-groups/1/dashboard/') payload = { group, week_start: '2026-08-31', week_end: '2026-09-06', members: [1, 2].map(id => ({ id, name: `学习者${id}`, is_current_user: id === userId, contract: null, completed_days: 0, current_streak: 0 })), pending_gaps: [], evidence_options: [{ ...evidence, plan_title: 'Python', day_number: 2 }] }
    else if (path === '/study-groups/1/result-card/') payload = null
    else if (path === '/team-challenges/') payload = challenges
    else if (path === '/team-challenges/1/contribute/') {
      const submitted = request.postDataJSON()
      payload = { id: userId, user_id: userId, user_name: `学习者${userId}`, role: submitted.role, role_label: submitted.role === 'explain' ? '讲解' : '复现', summary: submitted.summary, evidence_id: evidence.id, evidence_title: evidence.title, evidence_detail: evidence }
      challenges[0].entries = [...challenges[0].entries.filter(item => item.user_id !== userId), payload]
    }
    else return route.fulfill({ status: 404, json: { detail: `未预期的请求：${path}` } })
    return route.fulfill({ json: payload })
  })
  return { writes, errors, progress, evidence }
}

test('路线搜索使用标题、简介和适合人群，清空后恢复列表', async ({ page }) => {
  const state = await preparePage(page)
  const plans = [
    { id: 1, slug: 'python', title: 'Python 基础', summary: '变量与对象', audience: '零基础学习者', total_days: 30, estimated_weeks: 5, creator_name: '知序' },
    { id: 2, slug: 'git', title: 'Git 协作', summary: '分支与合并', audience: '团队开发者', total_days: 14, estimated_weeks: 2, owned: true, review_status: 'draft' },
  ]
  await page.route('**/api/plans/', route => route.fulfill({ json: plans }))
  await page.goto('/plans')
  const search = page.getByRole('searchbox', { name: '搜索路线' })
  await expect(page.locator('.plan-card')).toHaveCount(2)
  await expect(page.getByRole('navigation', { name: '主导航' }).getByRole('link', { name: '发现路线' })).toHaveAttribute('aria-current', 'page')
  await search.fill(' PYTHON ')
  await expect(page.locator('.plan-card')).toHaveCount(1)
  await expect(page.locator('.plan-card')).toHaveAttribute('href', '/plans/python')
  await search.fill('分支')
  await expect(page.locator('.plan-card')).toContainText('草稿')
  await search.fill('零基础')
  await expect(page.locator('.plan-card')).toContainText('Python 基础')
  await search.fill('不存在的主题')
  await expect(page.getByRole('heading', { name: '没有找到匹配的路线' })).toBeVisible()
  await page.getByRole('button', { name: '清除搜索' }).click()
  await expect(page.locator('.plan-card')).toHaveCount(2)
  await page.route('**/api/community/posts/9/', route => route.fulfill({ json: { id: 9, owned: true, title: '实验记录', content: '复现过程', post_type: 'share', plan: null, plan_day: null, images: [] } }))
  await page.goto('/community/posts/9/edit')
  await expect(page.getByLabel('标题', { exact: true })).toHaveValue('实验记录')
  await expect(page.locator('.main-nav a.active')).toHaveCount(1)
  await expect(page.locator('.main-nav a.active')).toHaveText('学习社区')
  expect(state.errors).toEqual([])
})

test('学习导航在桌面和手机均能直达内容并保留完成条件', async ({ page }) => {
  const state = await preparePage(page)
  await page.emulateMedia({ reducedMotion: 'reduce' })
  // 同一份长内容跨断点检查，避免仅靠极短的演示数据掩盖滚动和溢出问题。
  state.progress.day.content = { prerequisites: ['能运行上一节的实验'], learning_objectives: ['解释变量与对象的关系'], workflow: [{ title: '实验记录', body: '逐项核对输入、输出和失败条件。'.repeat(100) }] }
  for (const width of [1440, 1101, 1024, 821, 768, 390, 320]) {
    await page.setViewportSize({ width, height: 900 })
    await page.goto('/learn/1/2')
    const jumps = page.getByRole('navigation', { name: '本日学习导航' })
    await expect(jumps).toBeVisible()
    await expect(page.locator('.resume-note')).not.toHaveAttribute('open', '')
    expect(await page.locator('.lesson-orientation').evaluate(el => el.clientHeight >= el.scrollHeight)).toBe(true)
    await jumps.getByRole('button', { name: /学习证据/ }).click()
    await expect(page.locator('#lesson-evidence')).toBeFocused()
    await expect(page.locator('#lesson-evidence h2')).toBeInViewport()
    await jumps.getByRole('button', { name: /当日验收/ }).click()
    await expect(page.locator('#lesson-checkpoint')).toBeFocused()
    await expect(page.locator('#lesson-checkpoint h2')).toBeInViewport()
    await expect(page.getByRole('button', { name: '请先完成上方待办', exact: true })).toBeDisabled()
    await jumps.getByRole('button', { name: /知识点/ }).click()
    await expect(page.locator('#lesson-knowledge')).toBeFocused()
    await expect(page.locator('#lesson-knowledge h2')).toBeInViewport()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    for (const column of await page.locator('.lesson-content, .lesson-sidebar').all()) {
      expect(await column.evaluate(el => el.scrollWidth <= el.clientWidth + 2)).toBe(true)
    }
    if (width <= 820) {
      await page.getByRole('button', { name: '打开导航' }).click()
      await expect(page.getByRole('link', { name: '学习路径', exact: true })).toHaveAttribute('aria-current', 'page')
      await page.getByRole('button', { name: '关闭导航', exact: true }).click()
      await expect(page.getByRole('button', { name: '打开导航' })).toBeFocused()
      await expect(page.getByRole('link', { name: '学习路径', exact: true })).not.toBeVisible()
    }
  }
  for (const colorScheme of ['light', 'dark']) {
    await page.emulateMedia({ colorScheme })
    const colors = await page.locator('.global-ai-launcher span').evaluate(el => ({ ink: getComputedStyle(el).color, background: getComputedStyle(el).backgroundColor }))
    expect(colors.ink).not.toBe(colors.background)
    await expect(page.getByRole('button', { name: '打开全局 AI 学习助手' })).toBeInViewport()
    const heading = await page.locator('.lesson-heading h1').evaluate(el => ({ ink: getComputedStyle(el).color, expected: getComputedStyle(document.documentElement).color }))
    expect(heading.ink).toBe(heading.expected)
  }
  expect(state.writes.some(item => item.path.endsWith('/complete/'))).toBe(false)
  expect(state.errors).toEqual([])
})

test('短时记录、实验下载与私人成果草稿保持独立的完成和发布动作', async ({ page }, testInfo) => {
  const state = await preparePage(page)
  await page.goto('/learn/1/2')
  await page.getByLabel('可用时间').selectOption('30')
  await expect(page.getByText('画出两个变量的指向', { exact: true })).toBeVisible()
  await page.getByText('留下接续提示', { exact: true }).click()
  await page.getByLabel('下次从这里继续').fill('下次补空列表测试')
  await page.getByRole('button', { name: '保存本段进度' }).click()
  await expect.poll(() => state.progress.resume_note).toBe('下次补空列表测试')
  await page.reload()
  await page.getByText('查看或修改接续提示', { exact: true }).click()
  await expect(page.getByLabel('下次从这里继续')).toHaveValue('下次补空列表测试')
  await page.screenshot({ path: testInfo.outputPath('learning-page.png') })
  const downloaded = page.waitForEvent('download')
  await page.getByRole('button', { name: '下载 Python 案件' }).click()
  expect((await downloaded).suggestedFilename()).toBe('shared-list.py')
  await page.getByRole('button', { name: '选入私人成果展柜' }).click()
  await expect(page.getByRole('button', { name: '★ 已选入展柜' })).toBeVisible()
  await page.goto('/insights')
  await page.getByRole('button', { name: '整理为项目分享草稿' }).click()
  await expect(page.getByLabel('内容类型')).toHaveValue('project')
  await expect(page.getByLabel('正文', { exact: true })).toHaveValue(/私人实验结果/)
  expect(state.writes.some(r => r.path.endsWith('/complete/') || r.path === '/community/posts/')).toBe(false)
  expect(state.errors).toEqual([])
})

test('知识点辅导先展示可编辑正文，用户发送后才附带上下文', async ({ page }) => {
  const state = await preparePage(page)
  await page.goto('/learn/1/2')
  await page.getByRole('button', { name: '详细学习', exact: true }).click()
  await page.getByRole('button', { name: '让 AI 辅导这个知识点' }).click()
  await expect(page.getByLabel('将发送的正文')).toHaveValue(/赋值让名字指向对象/)
  expect(state.writes.filter(r => r.path === '/ai/chats/1/messages/')).toHaveLength(0)
  await page.getByLabel('将发送的正文').fill('仅发送我确认过的知识点。')
  await page.getByRole('button', { name: '发送问题', exact: true }).click()
  await expect(page.getByText('先画出变量指向。', { exact: true })).toBeVisible()
  const sent = state.writes.find(r => r.path === '/ai/chats/1/messages/')
  expect(sent.body).toContain('focus_content')
  expect(sent.body).toContain('仅发送我确认过的知识点。')
  expect(sent.body).not.toContain('私人复盘')
  expect(state.errors).toEqual([])
})

test('三问全部选择后才可提交，讲解接力模板不会自动发布', async ({ page }) => {
  const state = await preparePage(page)
  await page.goto('/review')
  const submit = page.getByRole('button', { name: '提交答案并查看解析' })
  await expect(submit).toBeDisabled()
  await expect(page.getByText('提交后的解释')).toHaveCount(0)
  for (const fieldset of await page.locator('.recall-quiz fieldset').all()) await fieldset.getByLabel('选项 B').check()
  await submit.click()
  await expect(page.getByRole('heading', { name: '本次答对 3/3 题 · 熟练掌握' })).toBeVisible()
  const submitted = JSON.parse(state.writes.find(r => r.path === '/reviews/').body)
  expect(submitted.answers).toEqual({ 'question-1': 1, 'question-2': 1, 'question-3': 1 })
  expect(submitted.quiz_token).toBe('test-token')
  await page.goto('/team')
  await page.getByRole('button', { name: '用讲解接力模板发起' }).click()
  await expect(page.getByLabel('共同任务')).toHaveValue(/根据反馈修正说明/)
  expect(state.writes.some(r => r.path === '/team-challenges/')).toBe(false)
  expect(state.errors).toEqual([])
})

test('手机宽度可以滚动到实验和知识点辅导入口', async ({ page }, testInfo) => {
  const state = await preparePage(page)
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/learn/1/2')
  await page.getByRole('button', { name: '填写案件证据' }).click()
  await expect(page.getByPlaceholder('证据标题')).toHaveValue('案件一：被悄悄改写的原始清单')
  await page.getByRole('button', { name: '详细学习', exact: true }).click()
  await page.getByRole('button', { name: '让 AI 辅导这个知识点' }).click()
  await page.getByLabel('将发送的正文').fill('手机上确认的知识点')
  await page.getByRole('button', { name: '发送问题', exact: true }).click()
  await expect(page.getByText('先画出变量指向。', { exact: true })).toBeVisible()
  await page.screenshot({ path: testInfo.outputPath('mobile-ai.png') })
  await expect(page.getByRole('button', { name: '关闭学习助手', exact: true })).toBeInViewport()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  expect(state.errors).toEqual([])
})

test('慢网和保存失败时记录缺口不会覆盖接续草稿', async ({ page }) => {
  const state = await preparePage(page)
  let release
  const gate = new Promise(resolve => { release = resolve })
  let fail = false
  await page.route('**/api/progress/1/', async route => {
    await gate
    if (fail) return route.fulfill({ status: 503, json: { detail: '模拟保存失败' } })
    Object.assign(state.progress, route.request().postDataJSON())
    await route.fulfill({ json: state.progress })
  })
  try {
    await page.goto('/learn/1/2')
    await page.getByText('留下接续提示', { exact: true }).click()
    await page.getByLabel('下次从这里继续').fill('不能被旧快照覆盖')
    await page.getByPlaceholder('例如：无法解释取消传播').fill('慢网期间的新缺口')
    await page.getByRole('button', { name: '记录缺口', exact: true }).click()
    await expect(page.locator('.gap-list')).toContainText('慢网期间的新缺口')
    await expect(page.getByLabel('下次从这里继续')).toHaveValue('不能被旧快照覆盖')
    release()
    await expect.poll(() => state.progress.resume_note).toBe('不能被旧快照覆盖')
    fail = true
    await page.getByLabel('下次从这里继续').fill('失败后仍要保留的草稿')
    await page.getByPlaceholder('例如：无法解释取消传播').fill('保存失败后的新缺口')
    await expect(page.locator('.notice.error')).toContainText('模拟保存失败')
    await page.getByRole('button', { name: '记录缺口', exact: true }).click()
    await expect(page.getByLabel('下次从这里继续')).toHaveValue('失败后仍要保留的草稿')
    fail = false
    await page.getByRole('button', { name: '保存本段进度' }).click()
    await expect.poll(() => state.progress.resume_note).toBe('失败后仍要保留的草稿')
  } finally { release() }
})

test('链接作品进入可编辑草稿时保留作品地址', async ({ page }) => {
  const state = await preparePage(page)
  Object.assign(state.evidence, { content: '', url: 'https://example.com/my-work', is_featured: true })
  await page.goto('/insights')
  await page.getByRole('button', { name: '整理为项目分享草稿' }).click()
  await expect(page.getByLabel('正文', { exact: true })).toHaveValue(/https:\/\/example.com\/my-work/)
  expect(state.writes.some(item => item.path === '/community/posts/')).toBe(false)
})

test('两名小队成员能互读讲解、证据和复现反馈', async ({ browser }) => {
  const contexts = await Promise.all([browser.newContext(), browser.newContext()])
  const [first, second] = await Promise.all(contexts.map(context => context.newPage()))
  const challenges = [{ id: 1, title: '讲解接力', description: '讲解后按说明复现', status: 'open', status_label: '进行中', deadline: '2099-01-01T00:00:00Z', entries: [], can_complete: false, expired: false }]
  try {
    await preparePage(first, 1, challenges)
    await preparePage(second, 2, challenges)
    await first.goto('/team')
    await first.getByLabel('我的分工').selectOption('explain')
    await first.getByLabel('过程与结论').fill('复制外层列表之后再修改副本。')
    await first.getByRole('button', { name: '提交分工证据' }).click()
    await expect(first.locator('.challenge-entries')).toContainText('复制外层列表之后再修改副本。')
    await second.goto('/team')
    await expect(second.locator('.challenge-entries')).toContainText('复制外层列表之后再修改副本。')
    await second.getByText('查看证据：变量实验', { exact: true }).click()
    await expect(second.locator('.challenge-entries')).toContainText('私人实验结果')
    await second.getByLabel('我的分工').selectOption('reproduce')
    await second.getByLabel('过程与结论').fill('按说明复现成功，空列表也通过。')
    await second.getByRole('button', { name: '提交分工证据' }).click()
    await expect(second.locator('.challenge-entries')).toContainText('按说明复现成功，空列表也通过。')
    await first.reload()
    await expect(first.locator('.challenge-entries')).toContainText('按说明复现成功，空列表也通过。')
  } finally { await Promise.all(contexts.map(context => context.close())) }
})

test('过期的 AI 会话请求不能覆盖最后选择或知识点新对话', async ({ page }) => {
  await preparePage(page)
  const session = id => ({ id, title: `会话${id}`, credential: 1, provider: 'openai', adapter: 'openai_chat_completions', api_url: 'https://provider.example/v1/chat/completions', model: 'test-model', context_rounds: 8, max_output_tokens: 1024, teaching_mode: 'hint', messages: [] })
  await page.route('**/api/ai/chats/', route => route.fulfill({ json: [session(1), session(2)] }))
  let pending
  let initial
  await page.route('**/api/ai/chats/1/', route => {
    if (!initial) initial = route
    else return route.fulfill({ json: session(1) })
  })
  await page.route('**/api/ai/chats/2/', route => { pending = route })
  await page.goto('/learn/1/2')
  await page.getByRole('button', { name: '打开全局 AI 学习助手' }).click()
  await expect.poll(() => Boolean(initial)).toBe(true)
  await page.getByRole('navigation', { name: '历史对话' }).getByRole('button', { name: /会话1/ }).click()
  await expect(page.locator('#ai-tutor-title')).toHaveText('会话1')
  await page.getByPlaceholder('输入问题，可直接粘贴图片；Enter 发送，Shift+Enter 换行').fill('待发送问题')
  await page.getByRole('navigation', { name: '历史对话' }).getByRole('button', { name: /会话2/ }).click()
  await expect.poll(() => Boolean(pending)).toBe(true)
  // 初始加载的外层 finally 也必须尊重后来选择的会话，不能提前放开发送。
  await initial.fulfill({ json: session(1) })
  await page.evaluate(() => new Promise(requestAnimationFrame))
  await expect(page.getByRole('button', { name: '发送问题', exact: true })).toBeDisabled()
  await page.getByRole('navigation', { name: '历史对话' }).getByRole('button', { name: /会话1/ }).click()
  await expect(page.getByRole('button', { name: '发送问题', exact: true })).toBeEnabled()
  await pending.fulfill({ json: session(2) })
  await page.evaluate(() => new Promise(requestAnimationFrame))
  await expect(page.locator('#ai-tutor-title')).toHaveText('会话1')
  pending = null
  await page.getByRole('navigation', { name: '历史对话' }).getByRole('button', { name: /会话2/ }).click()
  await expect.poll(() => Boolean(pending)).toBe(true)
  await page.getByRole('button', { name: '关闭学习助手', exact: true }).click()
  await page.getByRole('button', { name: '详细学习', exact: true }).click()
  await page.getByRole('button', { name: '让 AI 辅导这个知识点' }).click()
  await pending.fulfill({ json: session(2) })
  await page.evaluate(() => new Promise(requestAnimationFrame))
  await expect(page.locator('#ai-tutor-title')).toHaveText('新对话')
  await expect(page.getByLabel('知识点标题')).toHaveValue('变量绑定')
})


test('知识标记失败可重试，慢网期间不会提前完成或被后续保存撤销', async ({ page }) => {
  const state = await preparePage(page)
  state.progress.acceptance_checks = [true]
  let pending
  await page.route('**/api/progress/1/', route => { pending = route })
  await page.goto('/learn/1/2')
  await page.getByRole('button', { name: '还需学习 1 个知识点 →', exact: true }).click()
  await expect(page.locator('#lesson-knowledge')).toBeFocused()
  await page.getByRole('button', { name: '详细学习', exact: true }).click()
  const mark = page.locator('dialog footer .secondary')
  await mark.click()
  await expect(mark).toHaveText('正在保存…')
  await expect(mark).toBeDisabled()
  await expect.poll(() => Boolean(pending)).toBe(true)
  await pending.fulfill({ status: 503, json: { detail: '暂时无法保存' } })
  await expect(page.locator('dialog [role="alert"]')).toContainText('暂时无法保存')
  await expect(mark).toHaveText('完成复现，标记已学习')
  expect(state.progress.knowledge_checks).toEqual([false])
  pending = null
  await mark.click()
  await expect.poll(() => Boolean(pending)).toBe(true)
  // 关闭详情后编辑验收，让普通保存排在知识标记之后，验证不会写回旧知识状态。
  await page.getByRole('button', { name: '关闭知识详情', exact: true }).click()
  await page.getByLabel('原列表保持不变').uncheck()
  const first = pending
  pending = null
  Object.assign(state.progress, first.request().postDataJSON())
  await first.fulfill({ json: state.progress })
  await expect.poll(() => Boolean(pending)).toBe(true)
  expect(pending.request().postDataJSON().knowledge_checks).toEqual([true])
  Object.assign(state.progress, pending.request().postDataJSON())
  await pending.fulfill({ json: state.progress })
  await expect(page.locator('.save-status')).toHaveText('学习记录已保存')
  await expect(page.locator('.completion-status [role="alert"]')).toHaveCount(0)
  await expect(page.getByRole('button', { name: '还需完成 1 项验收 →', exact: true })).toBeVisible()
  await page.reload()
  await expect(page.locator('.knowledge-progress-card strong')).toHaveText('1/1')
  expect(state.errors).toEqual([])
})

test('路线失败显示在对应操作附近，重试时显示处理中并清除旧错误', async ({ page }) => {
  await preparePage(page)
  const plan = { id: 1, slug: 'python', title: 'Python 基础', days: [], enrolled: false, review_status: 'approved', feedback_summary: { count: 0 } }
  await page.route('**/api/plans/python/', route => route.fulfill({ json: plan }))
  let pending
  await page.route('**/api/plans/python/enroll/', route => { pending = route })
  await page.goto('/plans/python')
  await page.getByRole('button', { name: '加入学习计划', exact: true }).click()
  await expect(page.getByRole('button', { name: '正在加入…', exact: true })).toBeDisabled()
  await expect.poll(() => Boolean(pending)).toBe(true)
  await pending.fulfill({ status: 503, json: { detail: '加入失败，请重试' } })
  await expect(page.getByRole('alert')).toHaveText('加入失败，请重试')
  pending = null
  await page.getByRole('button', { name: '加入学习计划', exact: true }).click()
  await expect(page.getByRole('alert')).toHaveCount(0)
  await expect.poll(() => Boolean(pending)).toBe(true)
  await pending.fulfill({ json: { id: 1, current_day: 2 } })
  await expect(page).toHaveURL(new RegExp('/learn/1/2$'))
  plan.enrolled = true
  await page.goto('/plans/python')
  await page.route('**/api/plans/python/feedback/', route => route.fulfill({ status: 503, json: { detail: '反馈保存失败' } }))
  await page.getByPlaceholder('哪一天最难？哪个任务最有帮助？').fill('希望多一点练习')
  await page.getByRole('button', { name: '提交反馈', exact: true }).click()
  await expect(page.locator('.plan-feedback [role="alert"]')).toHaveText('反馈保存失败')
  await expect(page.getByPlaceholder('哪一天最难？哪个任务最有帮助？')).toHaveValue('希望多一点练习')
})

test('帖子草稿取消离开后保留，刷新有保护，保存成功后正常跳转', async ({ page }) => {
  const state = await preparePage(page)
  await page.route('**/api/community/posts/', route => route.fulfill({ json: { id: 9 } }))
  await page.route('**/api/community/posts/9/', route => route.fulfill({ json: { id: 9, title: '学习记录', content: '实验结果', post_type: 'share', created_at: '2026-09-09T00:00:00Z', author: { name: '学习者', username: 'learner' }, like_count: 0, comment_count: 0, images: [], comments: [] } }))
  await page.goto('/community/new')
  await page.getByLabel('标题', { exact: true }).fill('学习记录')
  await page.getByLabel('正文', { exact: true }).fill('实验结果')
  let dialogs = 0
  page.on('dialog', async dialog => { dialogs += 1; await dialog.dismiss() })
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/community/new$'))
  await expect(page.getByLabel('正文', { exact: true })).toHaveValue('实验结果')
  expect(dialogs).toBe(1)
  expect(await page.evaluate(() => !window.dispatchEvent(new Event('beforeunload', { cancelable: true })))).toBe(true)
  await page.getByRole('button', { name: '发布分享', exact: true }).click()
  await expect(page).toHaveURL(new RegExp('/community/posts/9$'))
  await expect(page.getByRole('heading', { name: '学习记录', exact: true })).toBeVisible()
  expect(dialogs).toBe(1)
  expect(await page.evaluate(() => window.dispatchEvent(new Event('beforeunload', { cancelable: true })))).toBe(true)
  expect(state.errors).toEqual([])
})

test('路线编辑只保护修改内容，撤销编辑和保存成功均可直接离开', async ({ page }) => {
  await preparePage(page)
  const plan = { slug: 'mine', title: '我的路线', subtitle: '', summary: '学习说明', audience: '', days: [{ day_number: 1, phase: '基础', week_title: '第一周', title: '变量', core_knowledge: '变量绑定', hands_on_task: '复现实验', acceptance_criteria: ['检查通过'], estimated_minutes: 60 }] }
  await page.route('**/api/my-plans/mine/', route => route.fulfill({ json: plan }))
  await page.route('**/api/plans/mine/', route => route.fulfill({ json: plan }))
  await page.goto('/plans/mine/edit')
  const title = page.getByLabel('路线名称', { exact: true })
  await expect(title).toHaveValue('我的路线')
  let dialogs = 0
  page.on('dialog', async dialog => { dialogs += 1; await dialog.dismiss() })
  await title.fill('修改后的路线')
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/plans/mine/edit$'))
  expect(dialogs).toBe(1)
  await title.fill('我的路线')
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/plans$'))
  expect(dialogs).toBe(1)
  await page.goBack()
  await title.fill('保存后的路线')
  await page.getByRole('button', { name: '保存修改', exact: true }).click()
  await expect(page).toHaveURL(new RegExp('/plans/mine$'))
  expect(dialogs).toBe(1)
  await page.goto('/plans/new')
  await page.getByPlaceholder('可选，例如：独立完成一个带权限和测试的 Django API').fill('完成一个学习项目')
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/plans/new$'))
  expect(dialogs).toBe(2)
})

test('学习证据草稿和失败笔记可取消离开，重试后保存状态恢复', async ({ page }) => {
  const state = await preparePage(page)
  let fail = true
  await page.route('**/api/progress/1/', route => {
    if (fail) return route.fulfill({ status: 503, json: { detail: '连接暂时中断' } })
    Object.assign(state.progress, route.request().postDataJSON())
    return route.fulfill({ json: state.progress })
  })
  await page.goto('/learn/1/2')
  await page.getByPlaceholder('证据标题').fill('未提交的证据')
  let dialogs = 0
  page.on('dialog', async dialog => { dialogs += 1; await dialog.dismiss() })
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page.getByPlaceholder('证据标题')).toHaveValue('未提交的证据')
  expect(dialogs).toBe(1)
  await page.getByPlaceholder('证据标题').fill('')
  await page.getByText('留下接续提示', { exact: true }).click()
  await page.getByLabel('下次从这里继续').fill('从失败路径继续')
  await page.getByRole('button', { name: '保存本段进度' }).click()
  await expect(page.locator('.completion-status [role="alert"]')).toContainText('连接暂时中断')
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/learn/1/2$'))
  expect(dialogs).toBe(2)
  fail = false
  await page.getByRole('button', { name: '重试保存', exact: true }).click()
  await expect(page.locator('.save-status')).toHaveText('学习记录已保存')
  expect(state.progress.resume_note).toBe('从失败路径继续')
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/plans$'))
  expect(dialogs).toBe(2)
  await page.goBack()
  await page.getByPlaceholder('证据标题').fill('确认放弃的草稿')
  page.removeAllListeners('dialog')
  page.once('dialog', dialog => dialog.accept())
  await page.locator('.sidebar').getByRole('link', { name: '发现路线' }).click()
  await expect(page).toHaveURL(new RegExp('/plans$'))
  expect(state.errors).toEqual([])
})

test('完成条件逐项消失，全部保存后才可完成；空检查列表与后端规则一致', async ({ page }) => {
  const state = await preparePage(page)
  state.progress.evidence = []
  await page.route('**/api/evidence/', route => route.fulfill({ json: state.evidence }))
  await page.route('**/api/progress/1/complete/', route => route.fulfill({ json: { ...state.progress, status: 'completed' } }))
  await page.goto('/learn/1/2')
  await expect(page.locator('.completion-steps li')).toHaveCount(3)
  await page.getByRole('button', { name: '详细学习', exact: true }).click()
  await page.getByRole('button', { name: '完成复现，标记已学习', exact: true }).click()
  await expect(page.locator('.completion-steps li')).toHaveCount(2)
  await page.getByLabel('原列表保持不变').check()
  await expect(page.locator('.save-status')).toHaveText('学习记录已保存')
  await expect(page.locator('.completion-steps li')).toHaveCount(1)
  await page.getByRole('button', { name: '还需提交 1 项学习证据 →', exact: true }).click()
  await expect(page.locator('#lesson-evidence')).toBeFocused()
  await page.getByPlaceholder('证据标题').fill('验证完成')
  await page.getByRole('button', { name: '提交证据', exact: true }).click()
  await expect(page.locator('.completion-steps li')).toHaveCount(0)
  await expect(page.locator('.finish')).toBeEnabled()
  await page.locator('.finish').click()
  await expect(page).toHaveURL(/\/dashboard\?enrollment=1$/)
  state.progress.acceptance_checks = []
  state.progress.day.acceptance_criteria = []
  state.progress.evidence = [state.evidence]
  await page.goto('/learn/1/2')
  await expect(page.locator('.completion-steps li')).toHaveCount(0)
  await expect(page.locator('.finish')).toBeEnabled()
  expect(state.errors).toEqual([])
})

test('返回路线列表保留关键词、结果和加载后的滚动位置', async ({ page }) => {
  await preparePage(page)
  await page.setViewportSize({ width: 1100, height: 700 })
  const plans = Array.from({ length: 24 }, (_, id) => ({ id: id + 1, slug: 'route-' + id, title: 'Python 实验 ' + id, summary: '变量与对象', days: [] }))
  await page.route('**/api/plans/', async route => {
    await new Promise(resolve => setTimeout(resolve, 150))
    await route.fulfill({ json: plans })
  })
  await page.route('**/api/plans/route-12/', route => route.fulfill({ json: plans[12] }))
  await page.goto('/plans')
  await page.getByRole('searchbox').fill('Python')
  await expect(page).toHaveURL(/q=Python/)
  const card = page.locator('.plan-card').nth(12)
  await card.scrollIntoViewIfNeeded()
  const scroll = await page.evaluate(() => scrollY)
  expect(scroll).toBeGreaterThan(0)
  await card.click()
  await expect(page).toHaveURL(new RegExp('/plans/route-12$'))
  await page.goBack()
  await expect(page.getByRole('searchbox')).toHaveValue('Python')
  await expect(page.locator('.plan-card')).toHaveCount(24)
  await expect.poll(() => page.evaluate(() => scrollY)).toBe(scroll)
})
