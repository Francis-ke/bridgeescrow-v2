#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")/.."
mkdir -p backups
backup_path="backups/bridgeescrow-$(date -u +%Y%m%dT%H%M%SZ).sql"
docker compose -f deploy/compose.yaml exec -T db sh -c \
  'export MYSQL_PWD="$MYSQL_ROOT_PASSWORD"; exec mysqldump --single-transaction --routines --triggers -uroot bridgeescrow' > "$backup_path"
printf 'Backup written to %s\n' "$backup_path"
