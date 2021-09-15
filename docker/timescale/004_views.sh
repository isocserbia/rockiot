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
   FROM ( SELECT row_number() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) AS rnum,
            sensor_data."time",
            sensor_data.device_id,
            sensor_data.temperature,
            abs(sensor_data.temperature - lag(sensor_data.temperature, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data
		   WHERE sensor_data.temperature != 0) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY (round((sd.diff / sd.temperature * 100::double precision)::numeric, 2)) DESC;


CREATE OR REPLACE VIEW public.lag_diff_humidity
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.humidity,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.humidity * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT row_number() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) AS rnum,
            sensor_data."time",
            sensor_data.device_id,
            sensor_data.humidity,
            abs(sensor_data.humidity - lag(sensor_data.humidity, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
            FROM sensor_data
			WHERE sensor_data.humidity != 0) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY (round((sd.diff / sd.humidity * 100::double precision)::numeric, 2)) DESC;


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
           FROM sensor_data
           WHERE sensor_data.no2 != 0) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_so2
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.so2,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.so2 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT row_number() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) AS rnum,
            sensor_data."time",
            sensor_data.device_id,
            sensor_data.so2,
            abs(sensor_data.so2 - lag(sensor_data.so2, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data
		   WHERE sensor_data.so2 != 0) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY (round((sd.diff / sd.so2 * 100::double precision)::numeric, 2)) DESC;


CREATE OR REPLACE VIEW public.lag_diff_pm1
 AS
 SELECT date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.pm1,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.pm1 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
		 	ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.pm1,
            abs(sensor_data.pm1 - lag(sensor_data.pm1, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data
           WHERE sensor_data.pm1 != 0) sd
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
           FROM sensor_data
           WHERE sensor_data.pm10 != 0) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;


CREATE OR REPLACE VIEW public.lag_diff_pm2_5
 AS
 SELECT
 	date_trunc('minute'::text, sd."time") AS "time",
    sd.device_id,
    sd.pm2_5,
    round(sd.diff::numeric, 2) AS diff,
    round((sd.diff / sd.pm2_5 * 100::double precision)::numeric, 2) AS diff_perc
   FROM ( SELECT
		    ROW_NUMBER() OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time" DESC) as rnum,
		 	sensor_data."time",
            sensor_data.device_id,
            sensor_data.pm2_5,
            abs(sensor_data.pm2_5 - lag(sensor_data.pm2_5, 1) OVER (PARTITION BY sensor_data.device_id ORDER BY sensor_data."time")) AS diff
           FROM sensor_data
           WHERE sensor_data.pm2_5 != 0) sd
  WHERE sd."time" >= (now() - '00:05:00'::interval) AND sd."time" <= now() AND sd.rnum < 2
  ORDER BY diff_perc DESC;

CREATE OR REPLACE VIEW public.lag_diff_device
 AS
	select
		  ldh.device_id,
		  ldh.time,
		  ldh.diff_perc as humidity_diff_perc,
		  ldt.diff_perc as temperature_diff_perc,
		  ldn.diff_perc as no2_diff_perc,
		  lds.diff_perc as so2_diff_perc,
		  ldp1.diff_perc as pm1_diff_perc,
		  ldp10.diff_perc as pm10_diff_perc,
		  ldp25.diff_perc as pm2_5_diff_perc,
		  msle.minutes_since_last_entry
	  from lag_diff_humidity ldh
	  join lag_diff_temperature ldt on ldh.device_id = ldt.device_id
	  join lag_diff_no2 ldn on ldh.device_id = ldn.device_id
	  join lag_diff_so2 lds on ldh.device_id = lds.device_id
	  join lag_diff_pm1 ldp1 on ldh.device_id = ldp1.device_id
	  join lag_diff_pm10 ldp10 on ldh.device_id = ldp10.device_id
	  join lag_diff_pm2_5 ldp25 on ldh.device_id = ldp25.device_id
	  join minutes_since_last_entry msle on ldh.device_id = msle.device_id
	  order by device_id desc;

EOF