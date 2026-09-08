# Git 版本管理与提交指南

> 核对日期：2026-09-06
> 项目目录：`D:\code\Python\Web_code\Study_myself`

## 当前事实与边界

- 本目录已经是 Git 仓库，核对时当前分支为 `main`，已配置 `origin`。本文更新只读核对本地状态，没有验证远程连通性、提交或推送；实际分支和未提交改动以 `git status` 为准。
- 根目录 `.env` 含本机配置；`secrets/*`、MySQL 数据、Redis 数据、上传文件、Conda 环境变量、虚拟环境、前端依赖和构建产物都不应进入 Git。
- `Study_myself` 中的 AI Fernet 主密钥保存在 Conda 环境变量，而不是项目文件。迁移数据库或部署已有用户配置时，必须通过安全渠道提供同一主密钥，否则已保存的 API Key 无法解密。
- 课程 JSON、源码、迁移和 Markdown 使用普通 Git 管理。需要提交大型二进制资产时再评估 LFS；历史文件体积检查不代表后续提交自动安全。
- 仓库已有 `.github/workflows/ci.yml`；远程平台启用 Actions 后会执行后端测试、迁移检查、生产安全检查、前端依赖审计和构建，以及后端、前端容器构建。

现有仓库先检查 `git status --short`、`git branch --show-current` 和 `git remote`；不要重新初始化或重复添加 `origin`。下面的初始化与连接远程章节仅供新环境首次建仓参考。公开仓库前还应单独确认课程内容许可、运营主体信息和隐私文本。

## 提交前验收

在 `Study_myself` Conda 环境中执行：

```powershell
cd D:\code\Python\Web_code\Study_myself\backend
$env:USE_SQLITE='1'
python -B manage.py test --noinput
Remove-Item Env:USE_SQLITE
python manage.py makemigrations --check --dry-run
python manage.py check
python -m pip check

cd ..\frontend
pnpm install --frozen-lockfile
pnpm audit --prod
pnpm build
node --test src/image.test.js
pnpm exec playwright install chromium
# 先在另一终端启动 Vite；此文件的 API 全部拦截。
pnpm exec playwright test learning-practice.spec.js --workers=1
# 真实后端回归另需隔离数据库、一次性普通用户和管理员、前后端以及 E2E_*。
pnpm exec playwright test app.spec.js
```

Docker 可用的机器还应执行：

```powershell
cd D:\code\Python\Web_code\Study_myself
docker build backend
docker build frontend
docker compose config
```

真实供应商 Key、邮件、TLS、备份恢复和部署机容量属于外部环境验收，不能用单元或浏览器冒烟结果代替。真实后端浏览器套件会写入业务数据；测试区别及实际结果见 [验收记录](./全功能回归验收记录-2026-08-28.md)。纯文档修改通常检查本地链接、源码对应关系和 `git diff --check` 即可，不必重新创建账号或运行全部业务测试。

## 新仓库的初始化和第一次提交（现有仓库跳过）

先配置只用于提交署名的 Git 身份；推荐仓库级配置，避免影响其他项目：

```powershell
cd D:\code\Python\Web_code\Study_myself
git init -b main
git config user.name "你的姓名或团队名"
git config user.email "你的提交邮箱"
```

确认本地秘密和生成物确实被忽略：

```powershell
git status --ignored --short
git check-ignore -v .env backend/media frontend/dist backend/.venv .playwright-mcp
```

然后暂存并审阅，不要直接使用 `git add -f` 绕过排除规则：

```powershell
git add .
git diff --cached --check
git diff --cached --stat
git status --short
git ls-files .env backend/media frontend/dist backend/.venv secrets/ai_credential_encryption_key
```

最后一条命令应没有输出。`secrets/README.md` 是说明文档，可以正常进入仓库；其他密钥文件不可以。

确认无误后提交：

```powershell
git commit -m "feat: establish learning platform and global AI tutor"
git tag -a v0.1.0 -m "首次可回归版本"
```

## 新仓库连接远程（已有 origin 时跳过）

在 GitHub、GitLab、Gitee 或自建 Git 服务创建空仓库，复制平台提供的 HTTPS 或 SSH 地址，再执行：

```powershell
git remote add origin <远程仓库地址>
git remote -v
git push -u origin main
git push origin v0.1.0
```

认证应使用平台的凭据管理器、个人访问令牌或 SSH Key，不能把密码或令牌写进远程 URL、脚本、`.env.example`、Git 配置文件或提交历史。

## 后续版本管理

- `main` 作为通过 CI 的集成分支；功能和修复使用短期分支，本项目 Codex 创建的分支默认使用 `codex/` 前缀，例如 `codex/learning-export`。分支名不改变测试和审查要求。
- 提交保持单一目的，推荐 `feat:`、`fix:`、`test:`、`docs:`、`refactor:`、`chore:` 前缀；数据库模型改动必须与对应迁移和测试放在同一提交。
- 合并前至少运行受影响测试和前端构建；发布版本使用语义化标签，例如 `v0.1.1`、`v0.2.0`。
- Git 只管理代码、迁移和文档，不管理 MySQL/Redis 运行数据。部署升级先备份，再运行迁移；回滚代码前先确认数据库迁移是否可逆。
- 一旦秘密误提交，不要只删除文件：立即轮换秘密、从历史中清除，并检查远程缓存、CI 日志和派生仓库。

## 现有工作区的提交审查

当前工作区包含学习增强代码、迁移、测试和文档改动。不要用 `git reset --hard`、`git clean` 或覆盖文件的方式清理未提交工作。先用 `git diff --stat` 和逐文件 diff 区分需求，再明确列出需要暂存的路径；上面的 `git add .` 仅适用于已经确认全部内容的新仓库首次提交。

学习增强发布应包含 `0017`、`practice.py`、相应前后端代码与回归测试；只提交模型而遗漏迁移，或只提交页面而遗漏后端字段，都会造成部署不一致。纯文档提交可单独使用 `docs:` 前缀，但不能把尚未提交的功能称为已发布版本。

提交前运行 `git diff --cached --check` 并审阅暂存内容；检查 `.env` 和实际 secret 文件未被跟踪。`secrets/README.md`、`.env.example` 应保留。构建产物与测试报告可作为本地交付或 CI 产物保留，按现有 `.gitignore` 不进入源码提交。

## 发布时仍需核对

1. 核对已配置远程的仓库可见性、维护者权限和目标分支。
2. 核对提交署名、暂存范围及密钥排除规则。
3. 在装有 Docker 的环境验证 Compose 和镜像构建。
4. 推送后确认 MySQL/Redis + Playwright CI 步骤在远程 runner 实际通过；本地代码存在 CI 定义不等于远程执行成功。
5. 使用轮换后的真实低权限供应商 Key 验证文本、图片和文件对话，再删除测试配置与会话。
