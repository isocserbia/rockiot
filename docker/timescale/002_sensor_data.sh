#!/bin/bash

psql --username "postgres" <<EOF
CREATE DATABASE rock_iot WITH OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE rock_iot TO postgres;

\c rock_iot
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS sensor_data (
  time          TIMESTAMP         NOT NULL,
  device_id     TEXT              NOT NULL,
  client_id     TEXT              NOT NULL,
  temperature   DOUBLE PRECISION,
  humidity      DOUBLE PRECISION,
  no2           DOUBLE PRECISION,
  so2           DOUBLE PRECISION,
  pm1           DOUBLE PRECISION,
  pm10          DOUBLE PRECISION,
  PM2_5         DOUBLE PRECISION
);

SELECT create_hypertable('sensor_data', 'time');
CREATE INDEX IF NOT EXISTS sensor_data_device_id_time_ind ON sensor_data (device_id, time DESC);

EOF