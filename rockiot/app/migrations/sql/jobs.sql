SELECT cron.schedule('rockiot_compute_15m_rollups','*/5 * * * *', $$SELECT rockiot_compute_15m_rollups(now()-interval '15 minutes', now())$$);

SELECT cron.schedule('rockiot_compute_1h_rollups','*/20 * * * *', $$SELECT rockiot_compute_1h_rollups(now()-interval '1 hours', now())$$);

SELECT cron.schedule('rockiot_compute_4h_rollups','0 */1 * * *', $$SELECT rockiot_compute_4h_rollups(now()-interval '4 hours', now())$$);

SELECT cron.schedule('rockiot_compute_24h_rollups','0 */4 * * *', $$SELECT rockiot_compute_24h_rollups(now()-interval '24 hours', now())$$);

SELECT cron.schedule('rockiot_delete_successful_cron_jobs_executions','0 */12 * * *', $$SELECT rockiot_delete_successful_cron_jobs_executions(now()-interval '24 hours')$$);

SELECT cron.schedule('rockiot_delete_terminated_devices_connections','0 */1 * * *', $$SELECT rockiot_delete_terminated_devices_connections(now()-interval '2 hours')$$);
