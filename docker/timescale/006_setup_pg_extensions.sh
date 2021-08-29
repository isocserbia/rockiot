#!/bin/sh

set -e

cat <<EOT >> ${PGDATA}/postgresql.conf
shared_preload_libraries='timescaledb,pg_cron,pg_partman_bgw'
cron.database_name='${POSTGRES_DB:-postgres}'
pg_partman_bgw.interval = 3600
pg_partman_bgw.dbname='${POSTGRES_DB:-postgres}'
EOT

pg_ctl restart

psql --username "postgres" <<EOF

\c rock_iot
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_cron CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_partman CASCADE;

EOF