import { expect, test } from '@playwright/test'

const learner = {
  username: process.env.E2E_USER || '',
  password: process.env.E2E_PASSWORD || '',
}
const administrator = {
  username: process.env.E2E_ADMIN_USER || '',
  password: process.env.E2E_ADMIN_PASSWORD || '',
}

async function login(page, account) {
  await page.goto('/login')
  await page.getByLabel('用户名').fill(account.username)
  await page.getByLabel('密码').fill(account.password)
  await page.getByRole('button', { name: '进入今日学习' }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
}

test('匿名访问受保护页面时回到登录页', async ({ page }) => {
  let refreshRequestCount = 0
  page.on('request', (request) => {
    if (request.method() === 'POST' && request.url().endsWith('/api/auth/refresh/')) {
      refreshRequestCount += 1
    }
  })

  await page.goto('/community')
  await expect(page).toHaveURL(/\/login\?next=\/community$/)
  await expect(page.getByRole('heading', { name: '欢迎回来' })).toBeVisible()
  expect(refreshRequestCount).toBe(1)
})

test.describe('普通学习者', () => {
  test.skip(!learner.username || !learner.password, '需要提供 E2E_USER 与 E2E_PASSWORD。')

  test('可访问核心功能、不能进入管理中心并能打开全局 AI 配置', async ({ page }) => {
    await login(page, learner)
    await expect(page.getByRole('heading', { name: /准备好留下今天的证据了吗/ })).toBeVisible()
    await expect(page.getByRole('link', { name: '管理中心' })).toHaveCount(0)

    await page.goto('/plans')
    await page.locator('.plan-card').first().click()
    await page.getByRole('button', { name: /加入学习计划|继续这条路径/ }).click()
    await expect(page).toHaveURL(/\/learn\/\d+\/1$/)
    await expect(page.getByText('最终复现任务', { exact: true })).toBeVisible()

    const postTitle = '浏览器回归测试分享'
    await page.goto('/community/new')
    await page.getByLabel('标题').fill(postTitle)
    await page.getByLabel('正文').fill('这是一条由临时账号创建、用于验证社区发布链路的测试内容。')
    await page.getByRole('button', { name: '发布分享' }).click()
    await expect(page.getByRole('heading', { name: postTitle })).toBeVisible()
    await page.getByPlaceholder('补充一个具体观点、验证结果或解决思路……').fill('社区评论链路正常。')
    await page.getByRole('button', { name: '参与讨论' }).click()
    await expect(page.getByText('社区评论链路正常。')).toBeVisible()
    await page.locator('.like-button').click()
    await expect(page.locator('.like-button')).toContainText('♥ 1')

    await page.goto('/team')
    await expect(page.locator('.team-page')).toBeVisible()
    const initialGroupName = page.getByLabel('小队名称', { exact: true })
    if (await initialGroupName.count()) {
      await initialGroupName.fill('浏览器回归测试小队')
      await page.getByRole('button', { name: '创建小队' }).click()
    }
    await expect(page.getByRole('heading', { name: '浏览器回归测试小队' })).toBeVisible()

    const pages = [
      ['/plans', '选择一条值得走完的路'],
      ['/journey', /.+/],
      ['/community', '把学到的，讲给同行的人'],
      ['/review', '复习不是重读，是再次想起来'],
      ['/insights', '看见掌握，也看见缺口'],
      ['/mutual-help', '让学习者真正帮助学习者'],
      ['/team', '和朋友一起把本周走完'],
      ['/notifications', '需要你回应的学习动态'],
      ['/profile', '个人信息'],
    ]
    for (const [path, heading] of pages) {
      await page.goto(path)
      await expect(page.getByRole('heading', { name: heading, level: 1 })).toBeVisible()
      await expect(page.locator('.notice.error')).toHaveCount(0)
    }

    await page.goto('/admin/reviews')
    await expect(page).toHaveURL(/\/dashboard$/)

    await page.getByRole('button', { name: '打开全局 AI 学习助手' }).click()
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByRole('heading', { name: '连接模型服务' })).toBeVisible()
    await expect(page.getByLabel('API Base URL')).toBeVisible()
    await expect(page.getByLabel('API Key')).toBeVisible()
  })

  test('AI 输入框支持附件编辑、图片粘贴和 Enter 发送', async ({ page }) => {
    await login(page, learner)
    await page.route('**/api/ai/providers/', (route) => route.fulfill({
      json: {
        enabled: true,
        credential_storage_available: true,
        attachment_cache_ttl_seconds: 3600,
        attachment_max_files: 2,
        attachment_max_bytes: 4 * 1024 * 1024,
        providers: [{ id: 'openai', name: 'OpenAI 兼容', models: ['deepseek-v4-flash'], supports_images: true }],
      },
    }))
    await page.route('**/api/ai/credentials/', (route) => route.fulfill({
      json: [{
        id: 42,
        name: '浏览器测试模型',
        provider: 'openai',
        adapter: 'openai_chat_completions',
        api_url: 'https://provider.example/v1/chat/completions',
        model: 'deepseek-v4-flash',
        key_last_four: 'test',
      }],
    }))
    await page.route('**/api/ai/chats/', (route) => {
      if (route.request().method() === 'GET') return route.fulfill({ json: [] })
      return route.fulfill({
        status: 201,
        json: {
          id: 501,
          title: '剪贴板图片测试',
          credential: 42,
          provider: 'openai',
          adapter: 'openai_chat_completions',
          api_url: 'https://provider.example/v1/chat/completions',
          model: 'deepseek-v4-flash',
          context_rounds: 8,
          max_output_tokens: 1024,
          teaching_mode: 'hint',
          message_count: 0,
        },
      })
    })
    let sentMessageCount = 0
    await page.route('**/api/ai/chats/501/messages/', async (route) => {
      sentMessageCount += 1
      const imageMessage = sentMessageCount === 1
      await new Promise((resolve) => setTimeout(resolve, 300))
      return route.fulfill({
        status: 201,
        json: {
          user_message: { id: 600 + sentMessageCount * 2 - 1, role: 'user', content: imageMessage ? '分析这张图片' : '用回车发送', attachments: imageMessage ? [{ name: 'clipboard.png', kind: 'image' }] : [] },
          assistant_message: { id: 600 + sentMessageCount * 2, role: 'assistant', content: imageMessage ? '图片已收到。' : '回车发送已收到。', attachments: [] },
        },
      })
    })

    await page.getByRole('button', { name: '打开全局 AI 学习助手' }).click()
    const input = page.getByPlaceholder(/可直接粘贴图片/)
    await expect(input).toBeVisible()
    const pasteClipboardImage = () => input.evaluate(async (element) => {
      const canvas = document.createElement('canvas')
      canvas.width = 2
      canvas.height = 2
      canvas.getContext('2d').fillRect(0, 0, 2, 2)
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'))
      const clipboard = new DataTransfer()
      clipboard.items.add(new File([blob], 'clipboard.png', { type: 'image/png' }))
      element.dispatchEvent(new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: clipboard }))
    })
    await input.fill('分析这张图片')
    await pasteClipboardImage()
    await expect(page.getByText('1 个附件')).toBeVisible()
    await expect(page.getByText('clipboard.png', { exact: true })).toBeVisible()
    await page.getByRole('button', { name: '移除附件 clipboard.png' }).click()
    await expect(page.getByText('1 个附件')).toHaveCount(0)
    await expect(page.getByText('clipboard.png', { exact: true })).toHaveCount(0)
    await pasteClipboardImage()
    await expect(page.getByText('1 个附件')).toBeVisible()

    const send = page.getByRole('button', { name: '发送问题' })
    expect(await send.evaluate((element) => {
      const box = element.getBoundingClientRect()
      return document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2) === element
    })).toBe(true)
    let fileChooserOpened = false
    page.on('filechooser', () => { fileChooserOpened = true })
    const requestPromise = page.waitForRequest((request) => request.method() === 'POST' && request.url().endsWith('/api/ai/chats/501/messages/'))
    await send.click()
    await expect(input).toHaveValue('')
    await expect(page.locator('.ai-message.user').filter({ hasText: '分析这张图片' })).toBeVisible()
    await expect(page.getByText('学习助手正在分析…')).toBeVisible()
    const request = await requestPromise
    expect(request.postData()).toContain('clipboard.png')
    await expect(page.getByText('图片已收到。')).toBeVisible()
    expect(fileChooserOpened).toBe(false)

    await input.fill('用回车发送')
    await input.press('Shift+Enter')
    await expect(input).toHaveValue('用回车发送\n')
    await input.press('Backspace')
    const enterRequest = page.waitForRequest((nextRequest) => nextRequest.method() === 'POST' && nextRequest.url().endsWith('/api/ai/chats/501/messages/'))
    await input.press('Enter')
    await enterRequest
    await expect(page.getByText('回车发送已收到。')).toBeVisible()
  })
})

test.describe('管理员', () => {
  test.skip(!administrator.username || !administrator.password, '需要提供 E2E_ADMIN_USER 与 E2E_ADMIN_PASSWORD。')

  test('可以进入管理中心', async ({ page }) => {
    await login(page, administrator)
    await expect(page.getByRole('link', { name: '管理中心' })).toBeVisible()
    await page.goto('/admin/reviews')
    await expect(page.getByRole('heading', { name: '管理中心' })).toBeVisible()
    await expect(page.locator('.notice.error')).toHaveCount(0)
  })
})
