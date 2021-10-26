CREATE OR REPLACE VIEW sensor_data_day_average_facility AS
select f.code, sdr.time::timestamp,
    round(avg(sdr.temperature)::numeric, 2) as temperature,
    round(avg(sdr.humidity)::numeric,2) as humidity,
    round(avg(sdr.so2)::numeric,2) as so2,
    round(avg(sdr.no2)::numeric,2) as no2,
    round(avg(sdr.pm1)::numeric,2) as pm1,
    round(avg(sdr.pm2_5)::numeric,2) as pm2_5,
    round(avg(sdr.pm10)::numeric,2) as pm10
from sensor_data_rollup_24h sdr
join app_device d on sdr.device_id = d.device_id
join app_facility f on d.facility_id = f.id
group by f.code, sdr.time order by time desc;

CREATE OR REPLACE VIEW sensor_data_day_average_municipality AS
select m.code, sdr.time::timestamp,
    round(avg(sdr.temperature)::numeric, 2) as temperature,
    round(avg(sdr.humidity)::numeric,2) as humidity,
    round(avg(sdr.so2)::numeric,2) as so2,
    round(avg(sdr.no2)::numeric,2) as no2,
    round(avg(sdr.pm1)::numeric,2) as pm1,
    round(avg(sdr.pm2_5)::numeric,2) as pm2_5,
    round(avg(sdr.pm10)::numeric,2) as pm10
from sensor_data_rollup_24h sdr
join app_device d on sdr.device_id = d.device_id
join app_facility f on d.facility_id = f.id
join app_municipality m on f.municipality_id = m.id
group by m.code, sdr.time order by time desc;

CREATE OR REPLACE VIEW sensor_data_hour_average_facility AS
select f.code, sdr.time::timestamp,
    round(avg(sdr.temperature)::numeric, 2) as temperature,
    round(avg(sdr.humidity)::numeric,2) as humidity,
    round(avg(sdr.so2)::numeric,2) as so2,
    round(avg(sdr.no2)::numeric,2) as no2,
    round(avg(sdr.pm1)::numeric,2) as pm1,
    round(avg(sdr.pm2_5)::numeric,2) as pm2_5,
    round(avg(sdr.pm10)::numeric,2) as pm10
from sensor_data_rollup_1h sdr
join app_device d on sdr.device_id = d.device_id
join app_facility f on d.facility_id = f.id
group by f.code, sdr.time order by time desc;

CREATE OR REPLACE VIEW sensor_data_hour_average_municipality AS
select m.code, sdr.time::timestamp,
    round(avg(sdr.temperature)::numeric, 2) as temperature,
    round(avg(sdr.humidity)::numeric,2) as humidity,
    round(avg(sdr.so2)::numeric,2) as so2,
    round(avg(sdr.no2)::numeric,2) as no2,
    round(avg(sdr.pm1)::numeric,2) as pm1,
    round(avg(sdr.pm2_5)::numeric,2) as pm2_5,
    round(avg(sdr.pm10)::numeric,2) as pm10
from sensor_data_rollup_1h sdr
join app_device d on sdr.device_id = d.device_id
join app_facility f on d.facility_id = f.id
join app_municipality m on f.municipality_id = m.id
group by m.code, sdr.time order by time desc;