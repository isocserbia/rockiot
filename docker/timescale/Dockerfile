# FROM timescale/timescaledb:latest-pg12
# FROM timescale/timescaledb-postgis:latest-pg13
# FROM timescale/timescaledb-postgis:latest-pg12
# FROM rockiot/timescaledb-postgis-apacheonly
# FROM timescale/timescaledb-postgis:latest-pg13

FROM 13-oss

COPY 002_sensor_data.sh /docker-entrypoint-initdb.d/002_sensor_data.sh
COPY 003_views.sh /docker-entrypoint-initdb.d/003_views.sh
COPY 004_views.sh /docker-entrypoint-initdb.d/004_views.sh
COPY 005_grafana.sh /docker-entrypoint-initdb.d/005_grafana.sh
COPY 006_setup_pg_extensions.sh /docker-entrypoint-initdb.d/006_setup_pg_extensions.sh
COPY 010_sensor_data_rollup_tables.sh /docker-entrypoint-initdb.d/010_sensor_data_rollup_tables.sh
COPY 020_functions.sql /docker-entrypoint-initdb.d/020_functions.sql
COPY 021_cron_jobs.sql /docker-entrypoint-initdb.d/021_cron_jobs.sql

