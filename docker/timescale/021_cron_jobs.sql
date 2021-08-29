SELECT cron.schedule('rockiot_compute_5m_rollups','*/5 * * * *', $$SELECT rockiot_compute_5m_rollups(now()-interval '10 minutes', now())$$);

SELECT cron.schedule('rockiot_compute_1h_rollups','*/10 * * * *', $$SELECT rockiot_compute_1h_rollups(now()-interval '2 hours', now())$$);

SELECT cron.schedule('rockiot_compute_4h_rollups','0 */1 * * *', $$SELECT rockiot_compute_4h_rollups(now()-interval '4 hours', now())$$);

SELECT cron.schedule('rockiot_compute_24h_rollups','0 */4 * * *', $$SELECT rockiot_compute_24h_rollups(now()-interval '8 hours', now())$$);
