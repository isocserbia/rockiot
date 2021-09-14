select avg(msg_rate) from app_deviceconnection where msg_rate > 0;


select dc.id, dc.user, dc.client_id, dc.connected_at, sd.time as "last_entry", now() - sd.time as "since_last_entry"
from app_deviceconnection dc
join sensor_data sd on dc.user = sd.device_id and dc.client_id = sd.client_id
where dc.state = 'RUNNING'
and sd.time >= (select max(sd2.time) from sensor_data sd2 where sd2.device_id = sd.device_id and sd2.client_id = sd.client_id)
and (now() - sd.time) > '5 seconds'::interval;


SELECT q.user, q.client_id, q.msg_cnt, q.entries_cnt, q.msg_rate_rank, q.msg_cnt/q.entries_cnt FROM(
SELECT dc.user, dc.client_id, dc.msg_cnt,
		(SELECT COUNT(sd.*) FROM sensor_data sd WHERE dc.user = sd.device_id AND dc.client_id = sd.client_id AND sd.time >= dc.connected_at) as entries_cnt,
		RANK () OVER ( ORDER BY msg_cnt DESC) msg_rate_rank
FROM app_deviceconnection dc
WHERE dc.state = 'RUNNING'
AND dc.msg_cnt > 0) as q;


SELECT q.device_id, q.client_id, avg(q.diff) as "avg_ingest_interval", avg(q.diff_no2) as "avg_diff_no2" FROM (
SELECT
sd.device_id,
sd.client_id,
sd.time - lag(sd.time, 1) OVER (PARTITION BY sd.device_id, sd.client_id ORDER BY sd."time") AS diff,
abs(sd.no2 - lag(sd.no2, 1) OVER (PARTITION BY sd.device_id, sd.client_id ORDER BY sd."time")) AS diff_no2
FROM sensor_data sd
JOIN app_deviceconnection dc ON dc.client_id = sd.client_id
WHERE dc.state = 'RUNNING') q
GROUP BY q.device_id, q.client_id;


SELECT dc.user, count(*) "connections_in_last_24h"
FROM app_deviceconnection dc
WHERE dc.connected_at >= (now() - '24:00:00'::interval)
GROUP BY dc.user;

