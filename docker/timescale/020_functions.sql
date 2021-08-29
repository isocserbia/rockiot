CREATE OR REPLACE FUNCTION rockiot_compute_5m_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 5min rollups from % to % (excluded)', start_time, end_time;

INSERT INTO sensor_data_rollup_5m("time", device_id, temperature, humidity, no2, so2, pm10, pm25)
SELECT
   date_trunc('seconds', (time - timestamptz 'epoch') / 300) * 300 + timestamptz 'epoch' AS mnt,
   device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm25)::numeric, 4) as pm25
FROM sensor_data WHERE time >= start_time AND time <= end_time
GROUP BY mnt, device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_5m.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_5m.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_5m.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_5m.so2 + excluded.so2)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_5m.pm10 + excluded.pm10)/2)::numeric, 4),
   pm25 = ROUND(((sensor_data_rollup_5m.pm25 + excluded.pm25)/2)::numeric, 4);
END;
$function$;



CREATE OR REPLACE FUNCTION rockiot_compute_1h_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 1h rollups from % to % (excluded)', start_time, end_time;

INSERT INTO sensor_data_rollup_1h("time", device_id, temperature, humidity, no2, so2, pm10, pm25)
SELECT
   date_trunc('hour', time) AS hr,
   device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm25)::numeric, 4) as pm25
FROM sensor_data WHERE time >= start_time AND time <= end_time
GROUP BY hr, device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_1h.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_1h.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_1h.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_1h.so2 + excluded.so2)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_1h.pm10 + excluded.pm10)/2)::numeric, 4),
   pm25 = ROUND(((sensor_data_rollup_1h.pm25 + excluded.pm25)/2)::numeric, 4);
END;
$function$;



CREATE OR REPLACE FUNCTION rockiot_compute_4h_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 4h rollups from % to % (excluded)', start_time, end_time;

INSERT INTO sensor_data_rollup_4h("time", device_id, temperature, humidity, no2, so2, pm10, pm25)
SELECT
   date_trunc('hour', (time - timestamptz 'epoch') / 4) * 4 + timestamptz 'epoch' AS hr,
   device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm25)::numeric, 4) as pm25
FROM sensor_data WHERE time >= start_time AND time <= end_time
GROUP BY hr, device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_4h.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_4h.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_4h.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_4h.so2 + excluded.so2)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_4h.pm10 + excluded.pm10)/2)::numeric, 4),
   pm25 = ROUND(((sensor_data_rollup_4h.pm25 + excluded.pm25)/2)::numeric, 4);
END;
$function$;



CREATE OR REPLACE FUNCTION rockiot_compute_24h_rollups(start_time timestamptz, end_time timestamptz) RETURNS void LANGUAGE PLPGSQL AS $function$
BEGIN
  RAISE NOTICE 'Computing 24h rollups from % to % (excluded)', start_time, end_time;
INSERT INTO sensor_data_rollup_24h("time", device_id, temperature, humidity, no2, so2, pm10, pm25)
SELECT
   date_trunc('day', time) AS dy,
   device_id,
   ROUND(avg(temperature)::numeric, 4) as temperature,
   ROUND(avg(humidity)::numeric, 4) as humidity,
   ROUND(avg(no2)::numeric, 4) as no2,
   ROUND(avg(so2)::numeric, 4) as so2,
   ROUND(avg(pm10)::numeric, 4) as pm10,
   ROUND(avg(pm25)::numeric, 4) as pm25
FROM sensor_data WHERE time >= start_time AND time <= end_time
GROUP BY dy, device_id
ON CONFLICT (time, device_id)
DO UPDATE
SET
   temperature = ROUND(((sensor_data_rollup_24h.temperature + excluded.temperature)/2)::numeric, 4),
   humidity = ROUND(((sensor_data_rollup_24h.humidity + excluded.humidity)/2)::numeric, 4),
   no2 = ROUND(((sensor_data_rollup_24h.no2 + excluded.no2)/2)::numeric, 4),
   so2 = ROUND(((sensor_data_rollup_24h.so2 + excluded.so2)/2)::numeric, 4),
   pm10 = ROUND(((sensor_data_rollup_24h.pm10 + excluded.pm10)/2)::numeric, 4),
   pm25 = ROUND(((sensor_data_rollup_24h.pm25 + excluded.pm25)/2)::numeric, 4);
END;
$function$;