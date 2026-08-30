#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'Usage: RESTORE_CONFIRM=<backup-name> %s <backup-directory>\n' "$0" >&2
  exit 2
fi

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
backup_dir="$(cd -- "$1" && pwd)"
backup_name="$(basename -- "${backup_dir}")"

if [[ "${RESTORE_CONFIRM:-}" != "${backup_name}" ]]; then
  printf 'Refusing restore: set RESTORE_CONFIRM=%s after verifying the target.\n' "${backup_name}" >&2
  exit 2
fi

cd -- "${backup_dir}"
sha256sum --check SHA256SUMS
cd -- "${project_root}"

# 恢复会覆盖数据库；先生成当前快照，并保留现有媒体目录作为可回退副本。
bash "${project_root}/deployment/backup.sh"
docker compose stop frontend backend
docker compose up -d --wait db redis
docker compose exec -T db sh -c \
  'MYSQL_PWD="$(cat /run/secrets/mysql_root_password)" mysqladmin --user=root drop "$MYSQL_DATABASE" --force && MYSQL_PWD="$(cat /run/secrets/mysql_root_password)" mysqladmin --user=root create "$MYSQL_DATABASE"'
gzip -dc "${backup_dir}/database.sql.gz" | docker compose exec -T db sh -c \
  'MYSQL_PWD="$(cat /run/secrets/mysql_root_password)" mysql --user=root "$MYSQL_DATABASE"'

media_previous="${project_root}/backend/media.pre-restore-$(date -u +%Y%m%dT%H%M%SZ)"
if [[ -d "${project_root}/backend/media" ]]; then
  mv -- "${project_root}/backend/media" "${media_previous}"
fi
mkdir -p -- "${project_root}/backend/media"
tar -C "${project_root}/backend" -xzf "${backup_dir}/media.tar.gz"
docker compose run --rm --no-deps --user root backend chown -R 10001:10001 /app/media

docker compose run --rm release
docker compose up -d --wait backend frontend
printf 'Restore completed. Previous media retained at: %s\n' "${media_previous}"
