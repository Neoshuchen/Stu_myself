#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
backup_root="${BACKUP_DIR:-${project_root}/deployment/backups}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="${backup_root}/${timestamp}"

umask 077
mkdir -p -- "${target}"
cd -- "${project_root}"

docker compose exec -T db sh -c \
  'MYSQL_PWD="$(cat /run/secrets/mysql_root_password)" mysqldump --user=root --single-transaction --routines --triggers --events "$MYSQL_DATABASE"' \
  | gzip -9 > "${target}/database.sql.gz"

tar -C "${project_root}/backend" -czf "${target}/media.tar.gz" media
sha256sum "${target}/database.sql.gz" "${target}/media.tar.gz" > "${target}/SHA256SUMS"

printf 'Backup created: %s\n' "${target}"
