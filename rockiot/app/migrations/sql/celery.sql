--
-- Data for Name: django_celery_beat_crontabschedule; Type: TABLE DATA; Schema: public; Owner: postgres
--
INSERT INTO public.django_celery_beat_crontabschedule (id, minute, hour, day_of_week, day_of_month, month_of_year, timezone) VALUES (1, '10', '0', '*', '*', '*', 'UTC');
INSERT INTO public.django_celery_beat_crontabschedule (id, minute, hour, day_of_week, day_of_month, month_of_year, timezone) VALUES (2, '0', '4', '*', '*', '*', 'UTC');
--
-- Name: django_celery_beat_crontabschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--
SELECT pg_catalog.setval('public.django_celery_beat_crontabschedule_id_seq', 2, true);


--
-- Data for Name: django_celery_beat_intervalschedule; Type: TABLE DATA; Schema: public; Owner: postgres
--
INSERT INTO public.django_celery_beat_intervalschedule (id, every, period) VALUES (1, 10, 'seconds');
INSERT INTO public.django_celery_beat_intervalschedule (id, every, period) VALUES (2, 30, 'seconds');
INSERT INTO public.django_celery_beat_intervalschedule (id, every, period) VALUES (3, 1, 'minutes');
INSERT INTO public.django_celery_beat_intervalschedule (id, every, period) VALUES (4, 10, 'minutes');
INSERT INTO public.django_celery_beat_intervalschedule (id, every, period) VALUES (5, 60, 'minutes');
INSERT INTO public.django_celery_beat_intervalschedule (id, every, period) VALUES (6, 5, 'minutes');
--
-- Name: django_celery_beat_intervalschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--
SELECT pg_catalog.setval('public.django_celery_beat_intervalschedule_id_seq', 6, true);


--
-- Data for Name: django_celery_beat_periodictask; Type: TABLE DATA; Schema: public; Owner: postgres
--
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (4, 'RabbitMQ overview', 'app.tasks.get_overview', '[]', '{}', NULL, NULL, NULL, NULL, true, NULL, 0, '2021-09-22 17:05:53.492904+00', '', NULL, 5, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (5, 'Export raw data to CSV', 'app.tasks.export_raw_data_to_csv', '[]', '{}', NULL, NULL, NULL, NULL, true, NULL, 0, '2021-09-22 17:05:53.50152+00', '', 1, NULL, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (6, 'celery.backend_cleanup', 'celery.backend_cleanup', '[]', '{}', NULL, NULL, NULL, NULL, true, NULL, 0, '2021-09-22 17:06:00.22197+00', '', 2, NULL, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (2, 'RabbitMQ health check', 'app.tasks.check_system_health', '[]', '{}', NULL, NULL, NULL, NULL, true, '2021-09-22 17:18:00.355417+00', 24, '2021-09-22 17:18:05.760363+00', '', NULL, 4, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (1, 'RabbitMQ connections sync', 'app.tasks.update_connections', '[]', '{}', NULL, NULL, NULL, NULL, true, '2021-09-22 17:18:00.722811+00', 72, '2021-09-22 17:18:05.778318+00', '', NULL, 3, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (3, 'Clean and Calibrate raw data', 'app.tasks.clean_and_calibrate', '[]', '{}', NULL, NULL, NULL, NULL, true, '2021-09-22 17:18:00.29225+00', 12, '2021-09-22 17:18:05.795599+00', '', NULL, 6, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (7, 'Send platform attributes', 'app.tasks.send_platform_attributes', '[]', '{}', NULL, NULL, NULL, NULL, true, NULL, 0, '2021-09-22 17:18:05.795599+00', '', NULL, 3, NULL, true, NULL, NULL, '{}', NULL, 300);
--
-- Name: django_celery_beat_periodictask_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.django_celery_beat_periodictask_id_seq', 7, true);

--
-- Data for Name: django_celery_beat_periodictasks; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.django_celery_beat_periodictasks (ident, last_update) VALUES (1, '2021-09-22 17:06:00.219866+00');