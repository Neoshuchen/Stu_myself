# Git 版本管理与提交指南

> 核对日期：2026-08-28  
> 项目目录：`D:\code\Python\Web_code\Study_myself`

## 当前事实与边界

- 当前目录尚未初始化为 Git 仓库，也没有可用的远程仓库地址，因此本轮不执行 `git init`、提交或推送。
- 根目录 `.env` 含本机配置；`secrets/*`、MySQL 数据、Redis 数据、上传文件、Conda 环境变量、虚拟环境、前端依赖和构建产物都不应进入 Git。
- `Study_myself` 中的 AI Fernet 主密钥保存在 Conda 环境变量，而不是项目文件。迁移数据库或部署已有用户配置时，必须通过安全渠道提供同一主密钥，否则已保存的 API Key 无法解密。
- 当前排除本地环境与生成物后没有超过 5 MB 的项目文件，不需要 Git LFS。以后确需提交大模型权重、视频或大型二进制数据时再单独评估，不能直接塞入普通 Git 历史。
- 仓库已有 `.github/workflows/ci.yml`；远程平台启用 Actions 后会执行后端测试、迁移检查、生产安全检查、前端依赖审计和构建，以及后端、前端容器构建。

建议第一次使用空的私有远程仓库，不要让平台预先生成 README、`.gitignore` 或许可证，避免首推时产生无意义的两套历史。公开仓库前还应单独确认课程内容许可、运营主体信息和隐私文本。

## 首次提交前验收

在 `Study_myself` Conda 环境中执行：

```powershell
cd D:\code\Python\Web_code\Study_myself\backend
$env:USE_SQLITE='1'
python manage.py test
Remove-Item Env:USE_SQLITE
python manage.py makemigrations --check --dry-run
python manage.py check
python -m pip check

cd ..\frontend
pnpm install --frozen-lockfile
pnpm audit --prod
pnpm build
pnpm exec playwright install chromium
# 创建可整体删除的一次性普通用户和管理员、启动前后端并配置 E2E_* 后：
pnpm test:e2e
```

Docker 可用的机器还应执行：

```powershell
cd D:\code\Python\Web_code\Study_myself
docker build backend
docker build frontend
docker compose config
```

真实供应商 Key、邮件、TLS、备份恢复和部署机容量属于外部环境验收，不能用单元或浏览器冒烟结果代替。浏览器测试会写入业务数据，只能使用隔离库或可整体删除的一次性账号。

## 初始化和第一次提交

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

## 连接远程仓库

在 GitHub、GitLab、Gitee 或自建 Git 服务创建空仓库，复制平台提供的 HTTPS 或 SSH 地址，再执行：

```powershell
git remote add origin <远程仓库地址>
git remote -v
git push -u origin main
git push origin v0.1.0
```

认证应使用平台的凭据管理器、个人访问令牌或 SSH Key，不能把密码或令牌写进远程 URL、脚本、`.env.example`、Git 配置文件或提交历史。

## 后续版本管理

- `main` 只保留已经通过 CI 的可运行版本；功能和修复使用短期分支，例如 `feature/ai-credential-switching`、`fix/session-key-binding`。
- 提交保持单一目的，推荐 `feat:`、`fix:`、`test:`、`docs:`、`refactor:`、`chore:` 前缀；数据库模型改动必须与对应迁移和测试放在同一提交。
- 合并前至少运行受影响测试和前端构建；发布版本使用语义化标签，例如 `v0.1.1`、`v0.2.0`。
- Git 只管理代码、迁移和文档，不管理 MySQL/Redis 运行数据。部署升级先备份，再运行迁移；回滚代码前先确认数据库迁移是否可逆。
- 一旦秘密误提交，不要只删除文件：立即轮换秘密、从历史中清除，并检查远程缓存、CI 日志和派生仓库。

## 当前仍需人工完成

1. 决定远程平台、仓库可见性和维护者权限。
2. 提供 Git 提交署名及空远程仓库地址。
3. 在装有 Docker 的环境验证 Compose 和镜像构建。
4. 推送后确认新增的 MySQL/Redis + Playwright CI 步骤在远程 runner 通过；本机没有 Docker，不能替代该验证。
5. 使用轮换后的真实低权限供应商 Key 验证文本、图片和文件对话，再删除测试配置与会话。
