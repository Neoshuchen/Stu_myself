# 知序

把长期学习目标变成每天可执行、可验证的任务。项目采用前后端分离架构：Vue 3 + Vite 前端、Django REST Framework 后端、MySQL 8 数据库。

当前项目定位是供本人和少量朋友共同使用的私有督学型学习平台，不以商业运营为目标。系统强调“真实完成、留下证据、延迟复习、朋友反馈”，不使用纯登录积分、全站排行榜或积分商城代替学习效果。

## 当前状态与质量边界

- 课程内容版本：8；系统课程运行时从 MySQL 读取，版本化 JSON 只用于初始化和受控更新。
- 趣味化第一阶段：间隔复习、证据成长、六类徽章、阶段 Boss 节点和路线地图。
- 小队扩充第一阶段：邀请制小队、周契约、共享进度、知识缺口朋友验证、通知和真实活动日历。
- 小队扩充第二阶段：多人分工协作挑战、证据合并结算和个人周成果卡。
- 全局 AI 学习助手：采用会话侧栏、紧凑模型栏和底部输入区；用户可按账号加密保存、编辑和切换多条 OpenAI 兼容 / Responses / Anthropic 模型服务，支持 OpenCode 风格 Base URL、4/8/12 轮上下文，以及选择或直接粘贴图片并读取 PDF、文本和源码。附件发送前可单独移除或整体替换，Enter 发送、Shift+Enter 换行；提交后输入框立即清空，问题先进入对话区，失败时恢复未发送内容。
- AI 辅助 Markdown 路线：用户可在创建路线时一次上传多个完整 `.md`、选择已有或新增账号模型配置，先查看知识主题、缺口、假设和风险，再编辑或放弃模型草稿；确认后可保存、加入个人规划或提交管理员公开审核。预览不落库，原始文档和模型原始响应不持久化。
- 2026-08-29 验证基线：107 项后端测试与 5 项 Playwright/Chromium 浏览器测试全部通过；迁移无遗漏，前端生产构建、真实 MySQL/Redis 启动和关键权限流程可用。浏览器已覆盖新增长期模型配置、多 Markdown 上传、诊断回填与私有草稿保存；真实供应商调用和部署机 Compose 流程仍需使用轮换后的低权限 Key 及 Docker 环境验收。

针对“几位朋友互相督促、按路线长期学习”的目标，当前能力已经达标。系统仍不是全自动教学或考试平台：固定授权实验资产、客观自动判题、内容版本回滚、管理质量看板、前端单元测试和更深的多用户浏览器流程仍待建设。课程事实和剩余边界见 [`课程内容质量与后续改进`](./docs/课程内容质量与后续改进.md)。

## 文档导航

| 文档 | 用途 |
|---|---|
| 本 README | 当前架构、本地开发、核心流程和课程导入的权威入口 |
| [`全功能回归验收记录`](./docs/全功能回归验收记录-2026-08-28.md) | 已执行测试、权限矩阵与尚未验证的外部边界 |
| [`课程内容质量与后续改进`](./docs/课程内容质量与后续改进.md) | 当前课程规模、已完成治理和仍有效的内容风险 |
| [`生产部署与运维手册`](./docs/生产部署与运维手册.md) | 发布、回滚、备份、监控、AI 隔离和上线门禁 |
| [`隐私与社区治理基线`](./docs/隐私与社区治理基线.md) | 用户数据、AI 第三方处理和社区处置规则 |
| [`Git 版本管理与提交指南`](./docs/Git版本管理与提交指南.md) | 首次建仓、提交审查和后续分支发布 |
| [`第四阶段规划`](./docs/第四阶段-上线前规模化能力开发规划.md) | 达到真实用户量与运营前置条件后才启动的能力 |
| [`AI 辅助 Markdown 路线生成设计`](./docs/AI辅助Markdown学习路线生成规划.md) | 已实现功能的数据流、接口、安全边界和验收记录 |

## 整体架构

```text
开发环境
浏览器 ── http://localhost:5173 ── Vite
  │                                  │ /api、/media 代理
  └──────────────────────────────────▼
                               Django :8000
                                │       │
                         持久业务数据   验证码/限流/缓存
                                │       │
                              MySQL    Redis

生产环境
浏览器 ── HTTPS/TLS 入口 ── Nginx(Vue 静态资源、限流、反向代理)
                                    │
                              Gunicorn + Django
                          ┌─────────┼─────────┐
                        MySQL      Redis    media 持久卷
```

| 层级 | 技术与职责 |
|---|---|
| 浏览器端 | Vue 3、Vue Router；页面按路由懒加载，访问令牌只保存在内存中 |
| 开发代理 | Vite 将 `/api` 和 `/media` 转发到 Django，前后端仍保持同一套接口路径 |
| 生产入口 | Nginx 提供 Vue 静态文件、CSP/安全响应头、认证接口限流和 Django 反向代理 |
| API 与业务 | Django 5.2、Django REST Framework；认证、权限、业务规则、聚合和受保护媒体签名 |
| 持久化 | MySQL 8.4 / utf8mb4；保存用户、课程、学习事实、社区、小队与通知 |
| 短期状态 | Redis；用于邮箱验证码、DRF 限流、缓存和就绪探针，不保存学习业务真相 |
| 文件 | `backend/media` 或生产 media 持久卷；附件通过短时签名和 Nginx internal location 读取 |
| 发布 | Docker Compose：MySQL、Redis、独立 release 任务、Gunicorn 后端、Nginx 前端 |

## 后端架构

后端采用模块化单体：`learning` 保持为稳定的 Django app 和数据库迁移边界，业务实现按领域拆分，避免账号、课程、社区和协作逻辑继续堆积在同一组大文件中。

```text
backend/learning/
├── accounts/          # 注册、认证、邮箱验证、个人资料
├── study/             # 学习路线、逐日进度、复习、洞察、课程正文
├── collaboration/     # 小队、契约、协作挑战、互评、答疑、搭子、通知
├── community/         # 帖子、评论、图片、举报
├── ai/                # 模型适配、会话、临时附件、凭据与 Redis 上下文
├── administration/    # 路线审核、用户治理
├── system/            # 健康检查、受保护媒体
├── services.py        # 跨领域复用的最小业务服务
├── models.py          # 稳定的数据模型与迁移边界
└── urls.py            # 直接组合各领域 API 的统一入口
```

`/api` 路径、DRF router basename、请求响应结构和数据库表名不随领域拆分变化；前端仍通过原有 API 地址访问后端。新增业务应进入对应领域，只有被两个以上领域共同使用且无法归属单一领域的逻辑才进入 `services.py`。

### 后端领域职责

| 领域 | 主要职责 | 代表数据或接口 |
|---|---|---|
| `accounts` | CSRF 会话建立、注册、登录、刷新、退出、邮箱验证、个人资料 | `/api/auth/*` |
| `study` | 路线、Markdown AI 预览、报名、逐日学习、证据、缺口、复习、成长、洞察、导出 | `LearningPlan`、`Enrollment`、`DayProgress`、`Evidence`、`Gap` |
| `collaboration` | 小队、周契约、协作挑战、通知、互评、答疑、搭子 | `StudyGroup`、`WeeklyContract`、`TeamChallenge`、`PeerReview` |
| `community` | 帖子、图片、评论、点赞、问题状态和举报 | `CommunityPost`、`CommunityComment`、`CommunityReport` |
| `ai` | 供应商白名单、BYOK、课程上下文、多模态消息与可丢失缓存 | `/api/ai/providers/`、`/api/ai/credentials/`、`/api/ai/chats/` |
| `administration` | 路线审核与正文维护、用户治理 | `/api/admin/plan-reviews/*`、`/api/admin/users/*` |
| `system` | 存活/就绪探针、短时签名媒体读取 | `/api/health/*`、`/api/media/*` |

`learning.models` 暂时作为单一 Django app 的模型和迁移边界保留。这样可避免仅为目录美观而改变表名、迁移依赖和反向关系；业务视图与序列化器按领域拆分，`urls.py` 和 SimpleJWT 配置直接引用职责模块，不保留无调用者的转发出口。新需求应先复用现有模型和事实数据，确有独立生命周期时再增加模型。

本轮架构复核删除了仅做导入转发的根 `views.py`、`serializers.py`。`models.py`、`tests.py` 与 `styles.css` 虽然较大，但分别仍是稳定迁移边界、现有全量回归集合和共享样式入口；在没有循环依赖、多人编辑冲突或构建性能证据前，机械拆文件只会增加导航成本。

### 请求处理层次

```text
URL / DRF Router
  → 领域 View / ViewSet：鉴权、权限边界、事务和流程编排
    → Serializer：输入清理、归属校验、输出契约
      → Model / QuerySet：持久事实和数据库约束
        → services.py / study.experience：跨接口复用的小型查询或派生计算
```

统计型数据优先实时从事实表派生。例如经验等级、徽章、活动日历和周成果卡不会维护第二份可被刷写或失真的累计值；真正需要历史留痕的行为才写入 `ReviewAttempt`、`Contribution`、`Notification` 等记录表。

## 前端架构

```text
frontend/src/
├── api.js             # API 基址、JWT 请求头、CSRF、401 单次刷新重试、错误归一化
├── auth.js            # 登录态恢复；access token 只驻留内存
├── router.js          # 页面懒加载、登录/管理员路由守卫
├── activeRoute.js     # 当前学习路线的轻量本地选择状态
├── components/        # AppShell、加载/空状态、学习日编辑器等复用组件
├── views/             # 路由页面；按学习、社区、互助、小队和管理功能组织
└── styles.css         # 全站设计变量、响应式布局和页面组件样式
```

页面不直接访问 MySQL、Redis 或课程 JSON，统一经 `api.js` 调用 Django。前端路由守卫只负责用户体验，真正的对象归属、管理员权限和小队成员权限始终由后端再次校验。Vite 开发与 Nginx 生产都使用相同的 `/api` 相对地址，避免维护两套请求代码。

## 数据来源与状态边界

| 数据 | 权威来源 | 说明 |
|---|---|---|
| 系统课程与每日正文 | MySQL | `system_roadmaps.v2.json` 只作为版本化导入源；导入后用户功能均从数据库读取 |
| 管理员正文修改 | MySQL | 修改日记录 `content_edited_at`，普通导入会跳过，`--force` 才允许覆盖 |
| 用户进度、证据、缺口和复习 | MySQL | 是完成判定、成长、洞察和成果卡的事实来源 |
| 小队、契约、挑战和通知 | MySQL | 权限由小队成员关系约束；结算采用事务和数据库唯一约束 |
| AI 会话文字、配置和附件元数据 | MySQL | 作为用户可删除的对话记录；不保存附件正文、图片本体或 API Key 明文 |
| AI 最近文本上下文、限时附件内容和请求锁 | Redis `ai` 缓存 | 可淘汰、可重建；图片和文件内容到期或重启后不再进入后续轮次，绝不是聊天权威存储 |
| Markdown 路线生成预览 | 当前请求与浏览器内存 | 原始 Markdown、诊断和未确认草稿不落库；只有用户确认后才写入现有路线表 |
| 邮箱验证码、限流和缓存 | Redis | 可丢弃短期状态；Redis 不可用时就绪探针失败，生产实例不应接收流量 |
| 附件与图片 | media 存储 | 数据库只存文件字段；外部访问必须经过短时签名接口 |
| access token | 浏览器内存 | 刷新页面后由 HttpOnly refresh Cookie 轮换恢复，不写 localStorage |

## 核心业务流程

### 1. 认证与会话

```text
打开页面 → GET /api/auth/csrf/ 建立 CSRF Cookie
  → 登录/注册 POST（CSRF + Nginx/DRF 双层限流）
  → access token 返回前端内存
  → refresh token 写入 HttpOnly、限定 /api/auth/ 路径的 Cookie
  → API 遇到 401 时只发起一次并发刷新
  → 刷新令牌轮换并拉黑旧令牌
  → 退出时服务端撤销刷新令牌并清除 Cookie
```

生产环境强制 HTTPS、安全 Cookie、明确域名和 CSRF 来源；缺少随机密钥、数据库密码或安全开关时配置会拒绝启动。

### 2. 每日学习闭环

```text
选择/加入路线 → Enrollment
  → 查看当前学习日 → 开始 DayProgress
  → 阅读知识卡并完成知识点检查、验收项
  → 提交 Evidence（内容、链接或受保护附件）
  → 记录 Gap 与失败过程
  → 全部检查通过且至少有一份证据 → 完成学习日
  → 推进 current_day → 更新活动日历、成长和复习队列
```

未来五天只读预习不会创建进度或提前完成任务。退出路线采用软退出，已有进度和证据保留，重新加入后继续原学习日。

### 3. 复习、缺口和成长

- 完成学习日后根据闭卷评分、未解决缺口和历史复习结果生成间隔复习时间。
- 复习结果分为“需要重学、基本想起、熟练掌握”，下一次间隔由统一规则计算。
- 知识缺口可补充解决过程和证据，再提交小队朋友验证；朋友可通过或退回并说明原因。
- 经验、等级和徽章从完成日、证据、已解决缺口、复习和公益贡献实时计算，不奖励纯登录。
- 路线地图按阶段分组，阶段最后一个学习日显示为 Boss 节点；当前节点、完成状态和可预习范围由报名进度决定。

### 4. 小队督学与第二阶段挑战

```text
创建小队 / 使用邀请码加入
  → 每位成员制定自己的自然周学习契约
  → 共享本周真实完成数、连续天数和待验证缺口
  → 发起限时 TeamChallenge
  → 2–4 人分别选择复现 / 测试 / 讲解 / 复核角色
  → 每人只能提交自己的既有 Evidence；同一角色只能一人承担
  → 至少两名成员完成不同分工
  → 事务内合并结算 → 每位参与者获得 Contribution → 全队收到 Notification
```

周成果卡实时聚合当前用户本周完成日、证据、已解决缺口、同伴互评、协作挑战和连续天数。分享由用户主动触发，只复制文字或调用系统分享面板，不生成公开个人页面。

### 5. 社区、互助与课程共建

- 用户可在全站社区或已加入路线的小组发布分享、问题、打卡和项目，支持图片、评论回复、点赞、解决状态和举报。
- 已提交证据的学习日可申请同伴互评；评审者检查正确性、可运行性和表达清晰度。
- 管理员可创建公开答疑场次，学习者提问，志愿者回答并形成贡献记录。
- 优质社区帖子可提交为某个学习日的课程补充，经管理员批准后进入数据库正文补充区。

### 6. 课程维护与管理员流程

```text
用户创建/Fork 路线草稿 → 编辑逐日内容 → 提交审核
  → 管理员查看完整正文与风险信息
  → 通过并发布 / 退回说明

系统课程更新 → 校验版本、字段、公开资源和私有来源
  → update_or_create 幂等导入
  → 跳过管理员人工编辑日（除非显式 --force）
```

管理员还可处理用户启停/删除、社区举报、课程补充和公开答疑。用户删除会按既有外键策略清理其学习与社区数据和附件；仍被他人学习的用户路线会保留并解除作者关联。

### 7. AI 学习助手

```text
任意登录页面点击全局「AI 学习助手」→ 选择账号已有配置，或填写协议、HTTPS Base URL、模型和 Key
  → 验证后把配置与当前用户绑定并加密保存，也可选择仅在本页临时使用
  → 可长期保留、编辑和切换多个模型服务；每个新会话绑定明确的配置 ID
  → 创建不依赖每日学习进度的个人会话，选择教学模式和上下文轮数
  → 可选上传图片、PDF、文本或源码 → 服务端校验、图片清洗、文本限量提取
  → 校验公网 HTTPS 目标并按协议非流式调用 → 成功后原子保存一问一答
  → MySQL 保留文字历史，Redis 缓存最近上下文与限时附件
```

新建全局会话不会自动绑定或读取每日课程、复盘、证据和缺口；旧版已经关联学习日的会话仍可继续读取当时的最小课程快照。AI 不修改知识检查、验收项、证据、缺口或完成状态。供应商失败时不写入半条消息；输出按纯文本展示，不执行 HTML、脚本、模型工具调用或上传文件中的指令。

### 8. AI 辅助 Markdown 路线

```text
创建路线 → 上传一个或多个完整 Markdown → 选择已有配置或从全局助手新增长期配置
  → POST /api/my-plans/markdown-preview/ 调用模型并校验结构
  → 查看诊断、修改逐日草稿或放弃
  → 用户确认后复用现有接口保存私有路线
      ├─ 加入自己的学习规划
      └─ 提交管理员审核，通过后进入公开路线
```

Markdown 和学习目标都作为不可信模型数据处理；截断文档、他人凭据、无效模型结构和供应商失败都不会创建路线。首版支持 1～30 天，未引入任务队列、专用路线模型或第二套社区。

## 主要页面与 API 分区

| 场景 | 前端页面 | 后端接口分区 |
|---|---|---|
| 今日学习与路线 | `/dashboard`、`/plans`、`/journey`、`/learn/...` | `/api/dashboard/`、`/api/plans/`、`/api/enrollments/`、`/api/progress/` |
| 证据、缺口、复习 | 学习页、`/review`、`/insights` | `/api/evidence/`、`/api/gaps/`、`/api/reviews/`、`/api/insights/` |
| AI 学习助手 | 所有登录页面的全局浮动入口 | `/api/ai/providers/`、`/api/ai/credentials/`、`/api/ai/chats/` |
| AI Markdown 路线 | `/plans/new` | `/api/my-plans/markdown-preview/`、`/api/my-plans/`、路线报名与审核接口 |
| 社区 | `/community`、帖子编辑与详情页 | `/api/community/posts/`、`comments/`、`reports/` |
| 互助 | `/mutual-help` | `/api/peer-reviews/`、`help-sessions/`、`buddy-profiles/` |
| 小队 | `/team` | `/api/study-groups/`、`weekly-contracts/`、`team-challenges/` |
| 通知 | `/notifications` | `/api/notifications/` |
| 管理 | `/admin/reviews` | `/api/admin/plan-reviews/`、`/api/admin/users/` |
| 运行状态 | 无业务页面 | `/api/health/live/`、`/api/health/ready/` |

## 工程合规与验证基线

这里的“合规”指项目自身的工程规范、安全基线和可部署性检查，不等同于第三方法律、等保或渗透测试认证。

### 代码与架构约束

- 后端采用模块化单体：保持一个稳定 Django app 和迁移边界，业务按领域拆分，不通过重复兼容层制造第二套实现。
- 公开 API 路径和前端路由保持稳定；权限校验位于后端对象查询和序列化层，不能只依赖前端隐藏按钮。
- 共享统计从事实数据实时派生；跨接口写入使用事务，挑战成员和角色使用数据库唯一约束防止重复结算。
- 新迁移必须先执行 `makemigrations --check --dry-run`，再在 release 阶段执行 `migrate`；Web 容器不自行迁移。
- `.env`、`secrets/*`、数据库转储、media、构建目录、虚拟环境和编辑器目录均被 `.gitignore` 排除。
- 课程导入校验会拒绝内部课件来源进入学习资料；仓库代码和文档中不保存服务器登录密码。

### 安全基线

- JWT access token 仅存内存；refresh token 使用 HttpOnly Cookie、轮换、黑名单和退出撤销。
- 写请求带 CSRF；正式环境限制可信来源、主机名和 HTTPS，Cookie、HSTS、CSP、防点击劫持和 MIME 嗅探策略已配置。
- Nginx 和 DRF 对认证及写接口分层限流；Redis 同时承载限流和验证码短期状态。
- 用户上传限制大小和 MIME 类型；图片会重新编码、限制尺寸并移除 EXIF；媒体使用短时签名，生产文件由 Nginx internal location 返回。
- 用户模型地址只接受解析到公网地址的 HTTPS URL，拒绝本机、内网、保留地址、URL 内嵌凭据和重定向；可用 `AI_CUSTOM_ALLOWED_HOSTS` 再收紧生产域名白名单。DNS 重绑定仍需部署侧出站网络策略兜底。请求超时、响应体、消息、上下文和附件均有硬上限，OpenAI Responses 请求显式使用 `store: false`。
- 临时 AI Key 只存在于当前页面和单次请求内存；保存模式必须使用独立 Fernet 主密钥，接口只返回末四位，不记录 Key、提示正文或附件正文到审计日志。
- Compose 中 Django 和 Nginx 以非 root 用户运行，后端只读根文件系统并启用 `no-new-privileges`；密钥通过 Docker secrets 文件注入。
- `/api/health/live/` 只检查进程；`/api/health/ready/` 同时验证 MySQL 和 Redis，避免依赖失效的实例继续接收流量。

### 2026-08-29 实际检查结果

后端 105/105、Playwright/Chromium 5/5 均通过；迁移检查、前端生产构建、真实 MySQL/Redis 启动和关键浏览器流程通过。Docker、真实邮件、轮换后的第三方模型 Key、TLS、备份恢复和外部告警仍须在对应环境验收。完整命令、权限矩阵与边界统一记录在 [`全功能回归验收记录`](./docs/全功能回归验收记录-2026-08-28.md)，README 不再维护第二份结果表。

## 本地开发

### 后端（Conda）

```powershell
conda create -n Study_myself python=3.13 -y
conda activate Study_myself
cd D:\code\Python\Web_code\Study_myself\backend
python -m pip install -r requirements.txt
```

注册验证码使用 Redis。本项目的 Windows 本地 Redis 可用 `D:\files\Redis\redis-server.exe --save "" --appendonly no` 启动，后端默认连接 `redis://127.0.0.1:6379/0`。开发环境默认把验证码邮件打印到后端终端；需要实际收信时，通过 Conda 环境变量配置腾讯云 SES API 凭证与已审核模板 ID。未配置 `TENCENT_SES_TEMPLATE_ID` 时仍会使用 Django 的 `EMAIL_BACKEND`，方便本地控制台和其它 SMTP 服务调试。

开发环境默认开启 AI 学习助手。登录后任意页面右下角都有全局入口；首次保存时需填写配置名称、接口协议、模型 Base URL、模型名称和供应商 Key。配置与用户账号绑定并保存在 MySQL，重新登录后仍可选择、编辑或删除；API Key 只以 Fernet 密文保存。启用持久配置时，为当前 Conda 环境配置独立 Fernet 密钥并重新激活环境：

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
conda env config vars set -n Study_myself AI_CREDENTIAL_ENCRYPTION_KEY=上一步输出的值
conda deactivate
conda activate Study_myself
```

本地 `Study_myself` 环境已于 2026-08-28 配置独立主密钥并应用 `learning.0016`；不要再次生成并覆盖该值，否则已经保存的 Key 将无法解密。主密钥不得提交仓库或与 Django `SECRET_KEY` 共用。

新建全局会话使用用户填写的模型名和公网 HTTPS Base URL。以 OpenAI 兼容协议为例，填写 `https://provider.example/v1` 即可，后端会补成 `/v1/chat/completions`；原来保存的完整请求地址仍然兼容。该行为与 [OpenCode 的 OpenAI-compatible 配置](https://opencode.ai/docs/providers) 和 [AI SDK 的 Base URL 契约](https://ai-sdk.dev/providers/openai-compatible-providers) 一致。`AI_OPENAI_MODELS`、`AI_ANTHROPIC_MODELS` 仅继续服务没有自定义地址的旧会话。服务端每次保存和调用前都会解析域名并拒绝非公网地址，生产环境还可用逗号分隔的 `AI_CUSTOM_ALLOWED_HOSTS` 只允许指定供应商域名，并应配合容器/防火墙出站策略防御 DNS 重绑定。默认单次最多 2 个、每个 4MB 的图片/PDF/文本/源码附件；图片会清除元数据，PDF 只读前 20 页，附件正文默认在 Redis 中最长缓存 1 小时。较大上传在请求处理期间可能进入 Django 临时上传文件，生产容器的 `/tmp` 是 tmpfs，请求结束后清理且不会进入 media 或备份。Redis 缓存会占用内存而不是“零存储”；多用户部署应通过 `AI_REDIS_URL` 使用独立、受容量限制的实例。

供应商调用失败时，先在模型配置中重新执行连接测试。`API Key 无效` 表示需要更新密钥；`账号已临时冻结` 表示供应商账号状态或额度异常，本地系统无法解除，需要前往供应商控制台处理或切换其他配置；普通权限拒绝还应核对所选模型是否对该账号开放。上游原始错误正文不会返回浏览器或写入日志。

在MySQL中创建 `zhixu` 数据库和最小权限账号后，将连接参数保存到Conda环境：

```powershell
conda env config vars set -n Study_myself MYSQL_DATABASE=zhixu MYSQL_USER=zhixu 'MYSQL_PASSWORD=your-password' MYSQL_HOST=127.0.0.1 MYSQL_PORT=3306
conda deactivate
conda activate Study_myself

cd D:\code\Python\Web_code\Study_myself\backend
python manage.py migrate
python manage.py import_curated_roadmaps
python manage.py createsuperuser
python manage.py runserver
```

用户提交的路线会进入“待审核”状态。网站管理员登录后访问前端 `/admin/reviews`，页面按「待审核路线 / 全部路线 / 用户管理 / 社区举报 / 课程共建 / 公开答疑」分栏，点击对应菜单切换；「全部路线」可以查看并编辑任意路线（含系统课程、草稿与未发布）每一天的完整正文，也能对路线改名、下架或删除（仍有学习者时删除需要二次确认）。只有 Django `is_staff` 用户可以访问该页面及其管理接口。

「用户管理」区块除了停用账号，还可以彻底删除普通用户：该用户的报名、逐日进度、学习证据（含 `media/evidence/<用户ID>/` 附件）、帖子、评论、点赞、举报、互评与答疑记录全部级联删除；他创建的学习路线如果还有其他人在学则保留下来（作者显示为“系统”），否则一并删除。删除不可撤销，只想阻止登录请用停用。管理员账号不能在这里删除，需要先在 Django 后台取消其管理员权限。

学习日正文和知识点都存在数据库里，直接在 `/admin/reviews` 的「全部路线」里点开某一天的「查看并编辑正文」修改：日级字段（标题、核心知识、实践任务、验收标准、预计时长、验证命令、参考实现）和每个知识点的 17 个字段（名称、一句话说明、解决什么问题、角色、基础概念、运行机制、相关工具、常见坑、实现要求、语言、运行命令、参考代码、预期结果、代码讲解、掌握标准、练习步骤、延伸资料）都可编辑，也能新增或删除知识点。保存后立即对学习者生效。管理员在学习路径页面看到未解锁的学习日时不再显示「可预习」，而是显示预计时长，点击直接打开同一个正文编辑器。

Django 自带的数据维护后台仍保留在后端 `/admin/`，它不是网站的管理员界面。

### 前端

```powershell
cd D:\code\Python\Web_code\Study_myself\frontend
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

开发服务器为 `http://localhost:5173`，Vite 会把 `/api` 和 `/media` 转发到 Django 的 `8000` 端口。后端只需使用 `python manage.py runserver`，前端只需使用 `pnpm dev`；MySQL 和 Redis 必须已启动且 Conda 环境变量正确。`Watching for file changes with StatReloader` 和 development server 警告均为正常提示：前者表示开发热重载已开启，后者提醒正式环境必须使用项目已有的 Gunicorn/Nginx 部署；日志配置会避免同一条自动重载信息重复输出，但不会隐藏生产安全警告。

### 自动化测试

测试配置使用临时 SQLite 和内存缓存，不会覆盖本地 MySQL 数据：

```powershell
cd D:\code\Python\Web_code\Study_myself\backend
$env:USE_SQLITE='1'
python manage.py test
python manage.py makemigrations --check --dry-run
Remove-Item Env:USE_SQLITE

cd ..\frontend
pnpm build
pnpm audit --prod

# 先在测试数据库创建一次性普通用户和管理员，并启动 Django 与 Vite。
pnpm exec playwright install chromium
$env:E2E_USER='一次性普通用户名'
$env:E2E_PASSWORD='一次性密码'
$env:E2E_ADMIN_USER='一次性管理员用户名'
$env:E2E_ADMIN_PASSWORD='一次性密码'
pnpm test:e2e
```

浏览器测试会真实创建报名、社区帖子/评论/点赞和小队数据，只能使用可整体删除的一次性账号，禁止指向生产库。CI 已配置隔离的 MySQL/Redis 和临时账号，并使用 Chromium 自动执行同一套测试；如需复用本机 Edge，可额外设置 `PLAYWRIGHT_CHANNEL=msedge`。

## Git 版本管理

当前目录尚未初始化 Git，也未配置远程仓库。首次提交前必须保持 `.env`、AI 加密主密钥、数据库、上传文件、虚拟环境、依赖和构建产物在版本控制之外；已有用户的加密配置迁移到其他环境时，Fernet 主密钥只能通过秘密管理渠道同步。

完整的验收、初始化、暂存检查、远程推送、分支和版本标签流程见 [`Git版本管理与提交指南`](./docs/Git版本管理与提交指南.md)。仓库已提供 [`.github/workflows/ci.yml`](./.github/workflows/ci.yml)，远程平台启用 CI 后会再次验证后端、前端和容器构建。

## 后续开发边界

社区、个人洞察、内容共建和学习小队的已实现行为已在上面的核心流程、页面/API 表和回归矩阵中说明，不在 README 维护重复功能清单。推荐、匿名统计和自动风控只有达到真实用户量与运营前置条件后才开发，具体触发条件见 [`第四阶段规划`](./docs/第四阶段-上线前规模化能力开发规划.md)。

## 生产部署

Compose 负责 MySQL、Redis、独立 release 任务、Django/Gunicorn 和前端 Nginx；生产默认关闭 AI，启用保存凭据时再叠加 `docker-compose.ai.yml`。完成 `.env`、`secrets/*`、media 权限和入口 TLS 配置后统一执行：

```bash
bash deployment/deploy.sh
```

生产配置缺少随机密钥、数据库密码、正式域名、HTTPS 或可信 CSRF 来源时会拒绝启动。发布、回滚、AI 隔离、HSTS、备份恢复、监控和令牌清理只在 [`生产部署与运维手册`](./docs/生产部署与运维手册.md) 维护，避免 README 与实际操作步骤分叉。

## 课程导入

系统课程正文保存在版本化目录 `backend/data/system_roadmaps.v2.json`，当前内容版本为 8，其中 Python 课程与示例以 3.12 为内容基线；生产镜像和新建 Conda 环境使用 Python 3.13，可正常覆盖该课程基线。目录包含一条 42 日采集/Web/Android 综合路线、十一条 30 日专项路线和一条 Git 7 日密集路线，共 379 个学习日。学习者参考资料只保留公开官方文档；`docs/详细学习课件/` 保存的是编排依据与上一版核验快照，不参与运行时导入。导入命令会校验内容版本、课程分类和私有资料地址，并使用 `update_or_create` 幂等更新全部十三条路线：

```powershell
python backend/manage.py import_curated_roadmaps
```

管理员在站点里改过正文的学习日会记录 `content_edited_at`，重新导入时默认跳过这些天并在输出里报告数量，避免把人工修改覆盖掉；确实要用 JSON 目录覆盖它们时加 `--force`（可配合 `--slug` 只处理一条路线）。路线缩短产生的旧学习日若已人工编辑或已有进度、社区讨论、改进建议，导入会中止并要求先迁移记录，不会级联误删数据。

每天的扩展内容、参考实现和验证命令可在前端管理中心或 Django `/admin/` 中继续维护。
