#!/bin/bash

psql --username "postgres" <<EOF

\c rock_iot

CREATE TABLE IF NOT EXISTS sensor_data_rollup_15m (
  time          TIMESTAMP         NOT NULL,
  device_id     TEXT              NOT NULL,
  temperature   DOUBLE PRECISION,
  humidity      DOUBLE PRECISION,
  no2           DOUBLE PRECISION,
  so2           DOUBLE PRECISION,
  pm1           DOUBLE PRECISION,
  pm10          DOUBLE PRECISION,
  pm2_5          DOUBLE PRECISION,
  CONSTRAINT sensor_data_rollup_15m_pkey PRIMARY KEY ("time", device_id)
);

SELECT create_hypertable('sensor_data_rollup_15m', 'time');
CREATE INDEX IF NOT EXISTS sensor_data_rollup_15m_device_id_time_ind ON sensor_data (device_id, time DESC);


CREATE TABLE IF NOT EXISTS sensor_data_rollup_1h (
  time          TIMESTAMP         NOT NULL,
  device_id     TEXT              NOT NULL,
  temperature   DOUBLE PRECISION,
  humidity      DOUBLE PRECISION,
  no2           DOUBLE PRECISION,
  so2           DOUBLE PRECISION,
  pm1           DOUBLE PRECISION,
  pm10          DOUBLE PRECISION,
  pm2_5          DOUBLE PRECISION,
  CONSTRAINT sensor_data_rollup_1h_pkey PRIMARY KEY ("time", device_id)
);

SELECT create_hypertable('sensor_data_rollup_1h', 'time');
CREATE INDEX IF NOT EXISTS sensor_data_rollup_1h_device_id_time_ind ON sensor_data (device_id, time DESC);


CREATE TABLE IF NOT EXISTS sensor_data_rollup_4h (
  time          TIMESTAMP         NOT NULL,
  device_id     TEXT              NOT NULL,
  temperature   DOUBLE PRECISION,
  humidity      DOUBLE PRECISION,
  no2           DOUBLE PRECISION,
  so2           DOUBLE PRECISION,
  pm1           DOUBLE PRECISION,
  pm10          DOUBLE PRECISION,
  pm2_5          DOUBLE PRECISION,
  CONSTRAINT sensor_data_rollup_4h_pkey PRIMARY KEY ("time", device_id)
);

SELECT create_hypertable('sensor_data_rollup_4h', 'time');
CREATE INDEX IF NOT EXISTS sensor_data_rollup_4h_device_id_time_ind ON sensor_data (device_id, time DESC);


CREATE TABLE IF NOT EXISTS sensor_data_rollup_24h (
  time          TIMESTAMP         NOT NULL,
  device_id     TEXT              NOT NULL,
  temperature   DOUBLE PRECISION,
  humidity      DOUBLE PRECISION,
  no2           DOUBLE PRECISION,
  so2           DOUBLE PRECISION,
  pm1           DOUBLE PRECISION,
  pm10          DOUBLE PRECISION,
  pm2_5          DOUBLE PRECISION,
  CONSTRAINT sensor_data_rollup_24h_pkey PRIMARY KEY ("time", device_id)
);

SELECT create_hypertable('sensor_data_rollup_24h', 'time');
CREATE INDEX IF NOT EXISTS sensor_data_rollup_24h_device_id_time_ind ON sensor_data (device_id, time DESC);


EOF