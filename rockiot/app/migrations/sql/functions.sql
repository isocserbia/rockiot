CREATE OR REPLACE FUNCTION rockiot_compute_15m_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 15min rollups from % to % (excluded)', start_time, end_time;

INSERT INTO sensor_data_rollup_15m("time", device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
SELECT
   date_trunc('seconds', (time - timestamptz 'epoch') / 900) * 900 + timestamptz 'epoch' AS mnt,
   sd.device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm1)::numeric, 4) as pm1,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm2_5)::numeric, 4) as pm2_5
FROM sensor_data sd
JOIN app_device ad on sd.device_id = ad.device_id
WHERE time >= start_time AND time <= end_time
AND ad.mode != 'CALIBRATION'
GROUP BY mnt, sd.device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_15m.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_15m.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_15m.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_15m.so2 + excluded.so2)/2)::numeric, 4),
   pm1 = ROUND(((sensor_data_rollup_15m.pm1 + excluded.pm1)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_15m.pm10 + excluded.pm10)/2)::numeric, 4),
   pm2_5 = ROUND(((sensor_data_rollup_15m.pm2_5 + excluded.pm2_5)/2)::numeric, 4);
END;
$function$;



CREATE OR REPLACE FUNCTION rockiot_compute_1h_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 1h rollups from % to % (excluded)', start_time, end_time;

INSERT INTO sensor_data_rollup_1h("time", device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
SELECT
   date_trunc('hour', time) AS hr,
   sd.device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm1)::numeric, 4) as pm1,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm2_5)::numeric, 4) as pm2_5
FROM sensor_data sd
JOIN app_device ad on sd.device_id = ad.device_id
WHERE time >= start_time AND time <= end_time
AND ad.mode != 'CALIBRATION'
GROUP BY hr, sd.device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_1h.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_1h.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_1h.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_1h.so2 + excluded.so2)/2)::numeric, 4),
   pm1 = ROUND(((sensor_data_rollup_1h.pm1 + excluded.pm1)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_1h.pm10 + excluded.pm10)/2)::numeric, 4),
   pm2_5 = ROUND(((sensor_data_rollup_1h.pm2_5 + excluded.pm2_5)/2)::numeric, 4);
END;
$function$;



CREATE OR REPLACE FUNCTION rockiot_compute_4h_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 4h rollups from % to % (excluded)', start_time, end_time;

INSERT INTO sensor_data_rollup_4h("time", device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
SELECT
   date_trunc('hour', (time - timestamptz 'epoch') / 4) * 4 + timestamptz 'epoch' AS hr,
   sd.device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm1)::numeric, 4) as pm1,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm2_5)::numeric, 4) as pm2_5
FROM sensor_data sd
JOIN app_device ad on sd.device_id = ad.device_id
WHERE time >= start_time AND time <= end_time
AND ad.mode != 'CALIBRATION'
GROUP BY hr, sd.device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_4h.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_4h.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_4h.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_4h.so2 + excluded.so2)/2)::numeric, 4),
   pm1 = ROUND(((sensor_data_rollup_4h.pm1 + excluded.pm1)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_4h.pm10 + excluded.pm10)/2)::numeric, 4),
   pm2_5 = ROUND(((sensor_data_rollup_4h.pm2_5 + excluded.pm2_5)/2)::numeric, 4);
END;
$function$;



CREATE OR REPLACE FUNCTION rockiot_compute_24h_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 24h rollups from % to % (excluded)', start_time, end_time;
INSERT INTO sensor_data_rollup_24h("time", device_id, temperature, humidity, no2, so2, pm1, pm10, pm2_5)
SELECT
   date_trunc('day', time) AS dy,
   sd.device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm1)::numeric, 4) as pm1,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm2_5)::numeric, 4) as pm2_5
FROM sensor_data sd
JOIN app_device ad on sd.device_id = ad.device_id
WHERE time >= start_time AND time <= end_time
GROUP BY dy, sd.device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_24h.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_24h.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_24h.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_24h.so2 + excluded.so2)/2)::numeric, 4),
   pm1 = ROUND(((sensor_data_rollup_24h.pm1 + excluded.pm1)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_24h.pm10 + excluded.pm10)/2)::numeric, 4),
   pm2_5 = ROUND(((sensor_data_rollup_24h.pm2_5 + excluded.pm2_5)/2)::numeric, 4);
END;
$function$;


CREATE OR REPLACE FUNCTION rockiot_delete_successful_cron_jobs_executions(since_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Deleting Successful Job Executions since %', since_time;
  DELETE FROM cron.job_run_details WHERE start_time <= since_time AND status='succeeded';
END;
$function$;


CREATE OR REPLACE FUNCTION rockiot_delete_terminated_devices_connections(since_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Deleting Terminated Devices Connections%', since_time;
  DELETE FROM public.app_deviceconnection WHERE state='TERMINATED' AND terminated_at IS NOT NULL AND terminated_at <= since_time;
END;
$function$;