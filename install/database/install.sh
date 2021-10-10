#!/bin/bash

apt-get -y install wget make gcc

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
apt-get update

apt-get -y install postgresql-12 postgresql-client-12

sh -c "echo 'deb [signed-by=/usr/share/keyrings/timescale.keyring] https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main' > /etc/apt/sources.list.d/timescaledb.list"
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/timescale.keyring
apt-get update

apt-get install  -y timescaledb-2-oss-postgresql-12=2.4.2~ubuntu18.04

apt-get install -y postgresql-12-postgis-2.5

apt-get -y install postgresql-12-cron

mkdir -p ./dbscripts
cp ../../docker/timescale/*.sql ./dbscripts
cd ./dbscripts

sudo -su postgres psql --username postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'rock_iot'" | grep -q 1 || sudo -su postgres psql --username postgres -tc "CREATE DATABASE rock_iot WITH OWNER postgres" && sudo -su postgres psql --username postgres -tc "GRANT ALL PRIVILEGES ON DATABASE rock_iot TO postgres;"

systemctl stop postgresql

chmod 644 /etc/postgresql/12/main/postgresql.conf

timescaledb-tune -yes

echo "host    all             postgres        172.31.46.61/32         trust" >> /etc/postgresql/12/main/pg_hba.conf
echo "listen_addresses = '*'" >> /etc/postgresql/12/main/postgresql.conf
echo "shared_preload_libraries = 'timescaledb,pg_cron'" >> /etc/postgresql/12/main/postgresql.conf
echo "cron.database_name = 'rock_iot'" >> /etc/postgresql/12/main/postgresql.conf

systemctl daemon-reload
systemctl start postgresql

systemctl status postgresql | grep inactive | [[ $(wc -l) == *1* ]] && echo "Service is NOT ACTIVE" || echo "Service is ACTIVE"
sleep 10
netstat -tunelp | grep 5432 | [[ $(wc -l) == *2* ]] && echo "Running OK" || echo "Not running"
sleep 3

sudo -su postgres psql --username postgres -d rock_iot -f 002_sensor_data.sql
sudo -su postgres psql --username postgres -d rock_iot -f 003_views.sql
sudo -su postgres psql --username postgres -d rock_iot -f 005_grafana.sql
sudo -su postgres psql --username postgres -d rock_iot -f 007_sensor_data_rollup_tables.sql

cd ../
rm -fR ./dbscripts

apt-get install -y prometheus-node-exporter prometheus-postgres-exporter

sudo apt-get install pgbackrest
exec sudo -u postgres /bin/sh - << eof

cat <<EOF > /etc/pgbackrest.conf
[main]
pg1-path=/var/lib/postgresql/12/main

[global]
repo1-path=/var/lib/pgbackrest
repo1-retention-full=2

[global:archive-push]
compress-level=3
EOF

echo "archive_mode = on" >> /etc/postgresql/12/main/postgresql.conf
echo "archive_command = 'pgbackrest --stanza=main archive-push %p'" >> /etc/postgresql/12/main/postgresql.conf
pgbackrest stanza-create --stanza=main
pgbackrest info --stanza=main

eof
