#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "${project_root}"

if [[ -n "$(docker compose ps --status running -q db 2>/dev/null)" ]]; then
  bash "${project_root}/deployment/backup.sh"
fi

docker compose build --pull
docker compose up -d --wait db redis
docker compose run --rm release
docker compose up -d --wait backend frontend

# 通过前端反向代理验证完整调用链，同时沿用生产环境的主机白名单。
health_host="$(docker compose exec -T backend printenv DJANGO_ALLOWED_HOSTS)"
health_host="${health_host%%,*}"
docker compose exec -T frontend wget \
  --header="Host: ${health_host}" \
  --header="X-Forwarded-Proto: https" \
  -qO- http://127.0.0.1:8080/api/health/ready/

printf '\nDeployment completed. Keep the previous image tags and backup until smoke tests pass.\n'
