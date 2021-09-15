#!/bin/bash

psql --username "postgres" <<EOF

\c rock_iot

CREATE OR REPLACE VIEW public.minutes_since_last_entry
 AS
 SELECT blah.device_id,
    (date_part('day'::text, now()::timestamp without time zone - blah.mtime) * 24::double precision + date_part('hour'::text, now()::timestamp without time zone - blah.mtime)) * 60::double precision + date_part('minute'::text, now()::timestamp without time zone - blah.mtime) AS minutes_since_last_entry
   FROM ( SELECT sensor_data.device_id,
            max(sensor_data."time") AS mtime
           FROM sensor_data
          GROUP BY sensor_data.device_id) blah;

CREATE OR REPLACE VIEW sensors_last_values AS
SELECT DISTINCT ON (device_id) device_id, client_id, time, temperature, humidity, no2, so2, pm1, pm10, pm2_5
FROM sensor_data
ORDER BY device_id, time DESC;

EOF