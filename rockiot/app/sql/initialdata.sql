INSERT INTO public.app_municipality(name, code, area, created_at, updated_at) VALUES
('Beograd', 'BGD', '0106000020E6100000010000000103000000010000000A0000000AC2F3FF7F7A34402781B94C9167464080D1F3FF2F613440D60A3ECF579246402839F4FFCFB23340DCE13D6793634640DCC6F3FF0F723440E04E9BC1792D4640D060F3FF9F1D35406C4FA64B965346400893F3FF3FC934402CD806A874824640E3CFF3FFFF63344070330AE65B904640DCC6F3FF0F723440C3F4730A90694640A5C3F3FFAF77344066AE01B0906846400AC2F3FF7F7A34402781B94C91674640', '2021-08-08 02:05:56.340766+00', '2021-08-08 02:05:56.340792+00');

INSERT INTO public.app_educationfacility(name, type, email, description, address, lon, lat, location, created_at, updated_at, municipality_id, code) VALUES
('Skola 1', 'ELEMENTARY_SCHOOL', 's1@bg.com', '', 'Blah blah 123', NULL, NULL, '0101000020E610000078C8F3FF3F6F3440A6C9D6A48E6B4640', '2021-08-08 02:06:43.301656+00', '2021-08-08 02:09:00.928629+00', 1, 'skola-1');

INSERT INTO public.app_educationfacility(name, type, email, description, address, lon, lat, location, created_at, updated_at, municipality_id, code) VALUES
('Skola 2', 'ELEMENTARY_SCHOOL', 's2@bg.com', '', 'Blah blah 123', NULL, NULL, '0101000020E610000078C8F3FF3F6F3440A6C9D6A48E6B4640', '2021-08-08 02:06:43.301656+00', '2021-08-08 02:09:00.928629+00', 1, 'skola-2');

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 1', 'SENSOR', '', 'Adr 1', 'device1', '4OrcNTFSZUrYX6NqP0P3lz', '2021-08-08 02:07:07.991904+00', '2021-08-09 18:59:10.966576+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000002FB4F3FFFF903440E6CA2CF4955B4640', NULL, 'device1pass', 1, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 2', 'SENSOR', '', 'Adr 2', 'device2', '1OrcNTFSZUrYX6NqP0P3ly', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device2pass', 1, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 3', 'SENSOR', '', 'Adr 3', 'device3', '3OrrNTFSGUrYX6NqP0P3ly', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device3pass', 1, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 4', 'SENSOR', '', 'Adr 4', 'device4', '41rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device4pass', 1, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 5', 'SENSOR', '', 'Adr 5', 'device5', '51rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device5pass', 1, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 6', 'SENSOR', '', 'Adr 6', 'device6', '61rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device6pass', 2, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 7', 'SENSOR', '', 'Adr 7', 'device7', '71rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device7pass', 2, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 8', 'SENSOR', '', 'Adr 8', 'device8', '81rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device8pass', 2, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 9', 'SENSOR', '', 'Adr 9', 'device9', '91rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device9pass', 2, NULL);

INSERT INTO public.app_device(name, type, description, address, device_id, device_key, created_at, updated_at, status, profile, metadata, lat, location, lon, device_pass, education_facility_id, ip_address) VALUES
('Device 10', 'SENSOR', '', 'Adr 10', 'device10', '10rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', NULL, '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', NULL, 'device10pass', 2, NULL);

INSERT INTO public.app_platform(name, description, created_at, updated_at) VALUES ('ROCKIOT', 'ROCKIOT platform', NOW(), NOW());

INSERT INTO public.app_serverattribute(name, value, description, created_at, updated_at, platform_id) VALUES ('INGEST_INTERVAL', '60', 'Ingest interval for sensor devices', NOW(), NOW(), 1);

INSERT INTO public.app_serverattribute(name, value, description, created_at, updated_at, platform_id) VALUES ('SSL_ENABLED', 'false', 'Indicates if devices should communicate with platform using SSL', NOW(), NOW(), 1);

INSERT INTO public.auth_group(name) VALUES ('RESEARCHER');

INSERT INTO public.auth_group(name) VALUES ('DEVICE_ADMIN');

INSERT INTO public.auth_group(name) VALUES ('DEVICE_INSTALLER');

INSERT INTO public.auth_group(name) VALUES ('PLATFORM_ADMIN');

INSERT INTO public.auth_group(name) VALUES ('CONNECTED_API_USER');

INSERT INTO public.auth_group(name) VALUES ('PUBLIC_API_USER');