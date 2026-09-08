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

test('短时记录、实验下载与私人成果草稿保持独立的完成和发布动作', async ({ page }, testInfo) => {
  const state = await preparePage(page)
  await page.goto('/learn/1/2')
  await page.getByLabel('可用时间').selectOption('30')
  await expect(page.getByText('画出两个变量的指向', { exact: true })).toBeVisible()
  await page.getByLabel('下次从这里继续').fill('下次补空列表测试')
  await page.getByRole('button', { name: '保存本段进度' }).click()
  await expect.poll(() => state.progress.resume_note).toBe('下次补空列表测试')
  await page.reload()
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
