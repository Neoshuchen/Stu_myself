# 生产密钥目录

部署前在本目录创建以下 UTF-8 纯文本文件，每个文件只放一个值且不要带引号：

- `django_secret_key`：至少 50 字符的随机值。
- `mysql_password`：应用数据库账号密码。
- `mysql_root_password`：仅用于数据库初始化、备份和恢复。
- `email_host_password`：不使用 SMTP 时创建空文件。
- `tencent_ses_secret_id`、`tencent_ses_secret_key`：不使用腾讯云 SES 时创建空文件。
- `ai_credential_encryption_key`：仅在使用 `docker-compose.ai.yml` 开启 AI Key 加密保存时创建的 Fernet 主密钥。可在已安装后端依赖的环境中运行 `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` 生成。

除本说明外，本目录全部内容已被 `.gitignore` 排除。Compose 会把这些本地文件直接挂载给不同的非 root 容器用户，Linux 服务器上应执行 `chmod 700 secrets && chmod 444 secrets/*`：主机上的其他账号无法穿透密钥目录，容器只能读取密钥文件且不能修改。

AI 主密钥与 Django 主密钥必须分开。轮换它会使已有 AI Key 无法解密：先关闭 AI，轮换文件并重启，再让用户删除旧记录并重新保存；不要把旧密钥或用户供应商 Key 写入仓库、`.env` 或日志。

更新配置后按 [部署手册](../docs/生产部署与运维手册.md) 重新创建服务，使开关与环境变量生效；单纯重启容器不会更新 Compose 注入的环境值。AI 关闭时会话和凭据管理接口也不可用，删除旧配置需在重新开启后进行。

数据库迁移或恢复已有用户配置时，需要原来的 Fernet 主密钥，不能重新生成替代。`deployment/backup.sh` 只备份数据库和媒体，不包含本目录；应通过独立的加密秘密备份渠道保留匹配密钥。密钥生成命令只供首次创建使用，切勿重定向覆盖现有文件。
