# 知序 · Zhixu

**把长期学习目标，变成每天可执行、可验证的行动。**

知序是一个面向个人自学与小队协作的学习管理平台。你可以沿着学习路线完成每日任务，用代码、笔记或实验结果记录成果，再通过间隔复习、同伴反馈和 AI 辅导巩固所学。

项目从自己与朋友的学习需求出发，围绕一个简单的流程构建：

**制定路线 → 动手学习 → 留下证据 → 闭卷复习 → 交流改进**

[功能介绍](#功能介绍) · [快速开始](#快速开始) · [部署](#部署) · [项目文档](#项目文档) · [参与贡献](#参与贡献)

## 功能介绍

| 功能 | 可以做什么 |
|---|---|
| 学习路线 | 使用内置路线、创建个人路线或从已有路线派生，按天查看知识点、实践任务与验收要求 |
| 每日学习 | 勾选知识点与验收项，提交代码、笔记、链接或附件，记录复盘与具体知识缺口 |
| 短时学习 | 按 15 / 30 / 60 分钟选择一个学习步骤，保存“下次从这里继续”的提示 |
| 复习与实验 | 接收到期复习任务，完成闭卷自评或客观题，下载 Python 故障案件并在本地修复 |
| 小队督学 | 通过邀请码组队，制定周契约，进行缺口验证、讲解接力和多人分工挑战 |
| 学习成果 | 查看路线地图、活动日历、成长徽章与个人洞察，精选作品并整理为社区分享草稿 |
| 社区与共建 | 发布分享与问题，参与评论、互评和答疑，提交课程改进建议 |
| AI 学习助手 | 接入自己的模型服务，围绕知识点提问，上传图片、PDF、文本或源码进行辅助学习 |
| Markdown 路线生成 | 上传 Markdown 资料，由所选模型生成可诊断、可编辑的路线草稿，确认后保存或提交公开审核 |
| 内容管理 | 管理员审核路线、维护每日正文、处理社区举报并管理用户 |

完成学习日需要全部知识点与验收项通过，并至少提交一份学习证据。短时学习、AI 回答和实验下载都不会自动标记整日完成。

AI 功能可选，使用者自行配置模型服务与 API Key。支持 OpenAI 兼容 Chat Completions、Responses 和 Anthropic Messages 协议；知识点内容先预览、后发送，路线生成先预览、后保存。

### 内置学习路线

当前课程目录包含 **13 条路线、379 个学习日**：

- **编程与工程**：Python 基础、爬虫基础、Git 全流程、AI Agent 工程、Coding Agent 工具链。
- **授权逆向分析**：JavaScript、Android、iOS，以及采集 / Web / Android 综合路线。
- **生活与通用能力**：个人财务与风险管理、健康管理与应急准备、沟通表达与问题解决、数字安全与信息素养。

首批客观练习覆盖 Python、HTTP 和 Git 的 5 个主题，共 15 道题；另有 3 份仅依赖标准库的 Python 实验案件。其余学习日使用课程实践与闭卷自评。网站不执行学习者上传的任意代码。

课程目录位于 [system_roadmaps.v2.json](backend/data/system_roadmaps.v2.json)，导入后由数据库提供页面内容。逆向与采集练习以本人资产或明确授权的样本为前提；生活类课程用于知识学习和流程练习。

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Vue 3、Vue Router、Vite |
| 后端 | Django 5.2、Django REST Framework |
| 数据库 | MySQL 8.4 |
| 缓存 | Redis |
| 认证与文件 | JWT、HttpOnly 刷新 Cookie、签名附件链接 |
| 部署 | Docker Compose、Gunicorn、Nginx |
| 测试 | Django TestCase、Playwright、Node.js 内置测试工具 |

后端采用模块化单体，按账号、学习、协作、社区、AI 和管理领域组织。前端通过统一的 `/api` 接口访问后端；MySQL 保存学习事实，Redis 保存验证码、限流和短期 AI 上下文。

## 快速开始

### 环境准备

使用 Python 3.13、Node.js 24 和项目锁定的 pnpm 版本，与当前容器和 CI 环境保持一致。安装并启动 MySQL 8.4 与 Redis，为项目创建使用 `utf8mb4` 的 `zhixu` 数据库，并准备拥有该数据库迁移与读写权限的账号。

下载仓库并进入项目根目录。以下命令均使用相对路径，数据库账号与密码请替换为自己的本地配置。

### 1. 安装后端依赖

```bash
python -m venv .venv
```

激活环境：

- Linux / macOS：`source .venv/bin/activate`
- Windows PowerShell：`.\.venv\Scripts\Activate.ps1`

已有 Conda 环境也可以直接使用，无需再创建虚拟环境。

```bash
python -m pip install -r backend/requirements.txt
```

### 2. 配置本地环境

Django 读取当前进程的环境变量，**不会自动加载根目录的 `.env`**。`.env.example` 用于 Compose 部署；其中的容器地址不应直接用于本地开发。

Linux / macOS：

```bash
export DJANGO_ENV=development
export DJANGO_DEBUG=1
export MYSQL_DATABASE=zhixu
export MYSQL_USER=zhixu
export MYSQL_PASSWORD='替换为本地数据库密码'
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export REDIS_URL=redis://127.0.0.1:6379/0
```

<details>
<summary>Windows PowerShell 配置方式</summary>

```powershell
$env:DJANGO_ENV='development'
$env:DJANGO_DEBUG='1'
$env:MYSQL_DATABASE='zhixu'
$env:MYSQL_USER='zhixu'
$env:MYSQL_PASSWORD='替换为本地数据库密码'
$env:MYSQL_HOST='127.0.0.1'
$env:MYSQL_PORT='3306'
$env:REDIS_URL='redis://127.0.0.1:6379/0'
```

</details>

这些变量只对当前终端及其子进程生效。在未配置邮件服务的开发环境中，注册验证码邮件默认输出到后端终端。

### 3. 初始化并启动后端

```bash
cd backend
python manage.py migrate
python manage.py import_curated_roadmaps
python manage.py createsuperuser
python manage.py runserver
```

后端默认运行在 `http://127.0.0.1:8000`。课程导入可以重复执行；已由管理员在线编辑的学习日默认跳过，不会被普通导入覆盖。

### 4. 启动前端

另开一个终端，从项目根目录运行：

```bash
cd frontend
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

打开 **http://localhost:5173**，使用刚创建的账号登录。Vite 会将 `/api` 请求代理到本地 Django 服务。

### 5. 开始学习

1. 在“学习路线”选择一条路线并加入，进入当天学习任务。
2. 阅读知识卡，完成实践并提交证据，记录尚不清楚的问题。
3. 完成当日验收，随后在复习中心巩固所学。
4. 邀请朋友组队，尝试周契约、缺口验证或讲解接力。

前端管理中心为 `/admin/reviews`，用于路线审核与正文维护；Django 数据后台位于后端的 `/admin/`。

## 配置 AI 助手

开发环境默认启用 AI 入口，生产 Compose 默认关闭。登录后可在全局学习助手中填写模型协议、HTTPS Base URL、模型名称和 API Key，选择临时使用或保存为账号配置。

保存 API Key 需要独立的 `AI_CREDENTIAL_ENCRYPTION_KEY`。首次配置时，可在已安装后端依赖的环境中生成 Fernet 主密钥：

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

将生成值通过环境变量或 secret 文件提供给后端，并在后续启动时保留同一值。已有加密配置的环境不要重新生成并覆盖主密钥，否则原有 API Key 无法解密。

保存的 API Key 以密文存储；临时 Key 不写浏览器持久存储。模型请求只接受经过校验的公网 HTTPS 地址。用户主动发送的文字或文件可能交由其选择的第三方模型服务处理，具体数据范围见 [隐私说明](docs/隐私与社区治理基线.md)。

## 部署

仓库提供 Docker Compose 配置，包含 MySQL、Redis、独立迁移任务、Django / Gunicorn 和 Nginx 前端。

按 [生产部署与运维手册](docs/生产部署与运维手册.md) 完成域名、TLS、`.env`、[密钥文件](secrets/README.md) 和媒体目录配置后，在部署环境的项目根目录执行：

```bash
bash deployment/deploy.sh
```

需要保存 AI 凭据及独立 AI 缓存时，使用手册中的 `docker-compose.ai.yml` 组合配置。备份、恢复、升级和故障排查也在部署手册中维护。

## 开发与测试

后端隔离测试，先从项目根目录进入后端目录：

```bash
cd backend
```

```bash
# Linux / macOS
USE_SQLITE=1 python -B manage.py test --noinput
```

```powershell
# Windows PowerShell
$env:USE_SQLITE='1'
python -B manage.py test --noinput
Remove-Item Env:USE_SQLITE
```

`USE_SQLITE=1` 仅对测试命令生效；日常运行和数据库迁移仍使用 MySQL。

前端检查，从 `frontend` 目录运行：

```bash
node --test src/image.test.js
pnpm build
pnpm exec playwright install chromium
# 在另一个终端保持 pnpm dev 运行
pnpm exec playwright test learning-practice.spec.js --workers=1
```

学习增强浏览器套件使用模拟 API，无需真实账号或模型服务。`app.spec.js` 另需真实后端、隔离数据库与一次性测试账号，会写入业务数据。完整配置与已执行结果见 [回归验收记录](docs/全功能回归验收记录-2026-08-28.md)；自动化流程见 [CI 配置](.github/workflows/ci.yml)。

## 项目结构

```text
.
├── backend/
│   ├── config/             # Django 配置
│   ├── data/               # 版本化课程目录
│   └── learning/           # 账号、学习、协作、社区、AI 与管理业务
├── frontend/
│   ├── src/                # Vue 页面、组件与 API 调用
│   └── e2e/                # 浏览器回归测试
├── docs/                   # 使用、课程维护、部署与验收文档
├── deployment/             # 发布、备份与恢复脚本
├── secrets/README.md        # 部署密钥配置说明
├── docker-compose.yml
└── docker-compose.ai.yml
```

## 项目文档

| 文档 | 内容 |
|---|---|
| [学习增强使用与验收](docs/学习增强使用与验收.md) | 六项学习增强的操作步骤、数据范围与常见问题 |
| [课程内容质量与维护](docs/课程内容质量与后续改进.md) | 课程来源、导入保护、练习维护和待改进项 |
| [AI Markdown 路线生成](docs/AI辅助Markdown学习路线生成规划.md) | 生成流程、输入约束、模型配置和审核机制 |
| [部署与运维](docs/生产部署与运维手册.md) | 配置、发布、升级、备份恢复与排障 |
| [隐私与社区治理](docs/隐私与社区治理基线.md) | 数据存储、AI 第三方处理及内容共享范围 |
| [回归验收记录](docs/全功能回归验收记录-2026-08-28.md) | 测试运行方法、历史结果和未验证范围 |
| [后续开发规划](docs/第四阶段-上线前规模化能力开发规划.md) | 推荐、全站统计和治理能力的扩展条件 |

## 参与贡献

欢迎通过 Issue 反馈使用问题、课程错误和功能建议，也欢迎提交 Pull Request。

- 问题反馈请附环境版本、操作步骤、预期结果和实际结果。
- 课程修订请说明适用主题、参考来源及可复现的验证方法。
- 代码改动请保持范围集中，补充相关验证；模型变更应包含对应迁移。
- 截图与日志请移除账号凭据、私人学习内容和签名附件地址。

提交前可参考 [Git 版本管理与提交指南](docs/Git版本管理与提交指南.md)。
