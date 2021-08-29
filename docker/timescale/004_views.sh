#!/bin/bash

psql --username "postgres" <<EOF

\c rock_iot

CREATE OR REPLACE VIEW public.lag_diff_temperature
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.temperature,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.temperature * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
			ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.temperature,
            abs(sensor_data.temperature - lag(sensor_data.temperature, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_humidity
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.humidity,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.humidity * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
			ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.humidity,
            abs(sensor_data.humidity - lag(sensor_data.humidity, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_no2
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.no2,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.no2 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
			ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.no2,
            abs(sensor_data.no2 - lag(sensor_data.no2, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_so2
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.so2,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.so2 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
			ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.so2,
            abs(sensor_data.so2 - lag(sensor_data.so2, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_pm10
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.pm10,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.pm10 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
		 	ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.pm10,
            abs(sensor_data.pm10 - lag(sensor_data.pm10, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_pm25
 AS
 SELECT
 	date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.pm25,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.pm25 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
		    ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.pm25,
            abs(sensor_data.pm25 - lag(sensor_data.pm25, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


EOF