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
  temperature   DOUBLE PRECISION  NOT NULL,
  humidity      DOUBLE PRECISION  NOT NULL,
  no2           DOUBLE PRECISION  NOT NULL,
  so2           DOUBLE PRECISION  NOT NULL,
  pm10          DOUBLE PRECISION  NOT NULL,
  pm25          DOUBLE PRECISION  NOT NULL
);

SELECT create_hypertable('sensor_data', 'time');
CREATE INDEX IF NOT EXISTS sensor_data_device_id_time_ind ON sensor_data (device_id, time DESC);

EOF