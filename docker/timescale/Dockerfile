# FROM timescale/timescaledb:latest-pg12
# FROM timescale/timescaledb-postgis:latest-pg13
# FROM timescale/timescaledb-postgis:latest-pg12
# FROM rockiot/timescaledb-postgis-apacheonly
# FROM timescale/timescaledb-postgis:latest-pg13

FROM 13-oss

COPY 001_create_db.sh /docker-entrypoint-initdb.d/
COPY 002_sensor_data.sql /docker-entrypoint-initdb.d/
COPY 003_views.sql /docker-entrypoint-initdb.d/
COPY 005_grafana.sql /docker-entrypoint-initdb.d/
COPY 006_setup_pg_extensions.sh /docker-entrypoint-initdb.d/
COPY 007_sensor_data_rollup_tables.sql /docker-entrypoint-initdb.d/
