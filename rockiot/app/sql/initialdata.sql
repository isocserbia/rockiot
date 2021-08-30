INSERT INTO public.app_municipality(name, code, area, created_at, updated_at) VALUES
('Beograd', 'BGD', '0106000020E6100000010000000103000000010000000A0000000AC2F3FF7F7A34402781B94C9167464080D1F3FF2F613440D60A3ECF579246402839F4FFCFB23340DCE13D6793634640DCC6F3FF0F723440E04E9BC1792D4640D060F3FF9F1D35406C4FA64B965346400893F3FF3FC934402CD806A874824640E3CFF3FFFF63344070330AE65B904640DCC6F3FF0F723440C3F4730A90694640A5C3F3FFAF77344066AE01B0906846400AC2F3FF7F7A34402781B94C91674640', '2021-08-08 02:05:56.340766+00', '2021-08-08 02:05:56.340792+00');

INSERT INTO public.app_facility(name, type, email, description, address, location, created_at, updated_at, municipality_id, code) VALUES
('Skola 1', 'ELEMENTARY_SCHOOL', 's1@bg.com', '', 'Blah blah 123', '0101000020E610000078C8F3FF3F6F3440A6C9D6A48E6B4640', '2021-08-08 02:06:43.301656+00', '2021-08-08 02:09:00.928629+00', 1, 'skola-1');

INSERT INTO public.app_facility(name, type, email, description, address, location, created_at, updated_at, municipality_id, code) VALUES
('Skola 2', 'ELEMENTARY_SCHOOL', 's2@bg.com', '', 'Blah blah 123', '0101000020E610000078C8F3FF3F6F3440A6C9D6A48E6B4640', '2021-08-08 02:06:43.301656+00', '2021-08-08 02:09:00.928629+00', 1, 'skola-2');

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 1', 'SENSOR', '', 'device1', '4OrcNTFSZUrYX6NqP0P3lz', '2021-08-08 02:07:07.991904+00', '2021-08-09 18:59:10.966576+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000002FB4F3FFFF903440E6CA2CF4955B4640', 'device1pass', 1);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 2', 'SENSOR', '', 'device2', '1OrcNTFSZUrYX6NqP0P3ly', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device2pass', 1);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 3', 'SENSOR', '', 'device3', '3OrrNTFSGUrYX6NqP0P3ly', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device3pass', 1);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 4', 'SENSOR', '', 'device4', '41rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device4pass', 1);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 5', 'SENSOR', '', 'device5', '51rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device5pass', 1);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 6', 'SENSOR', '', 'device6', '61rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device6pass', 2);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 7', 'SENSOR', '', 'device7', '71rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device7pass', 2);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 8', 'SENSOR', '', 'device8', '81rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device8pass', 2);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 9', 'SENSOR', '', 'device9', '91rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device9pass', 2);

INSERT INTO public.app_device(name, type, description, device_id, device_key, created_at, updated_at, status, profile, metadata, location, device_pass, facility_id) VALUES
('Device 10', 'SENSOR', '', 'device10', '10rrNEFSGUrYX6NqP0P3lg', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'NEW', 'DEFAULT', '{"supported_sensors": ["humidity"]}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device10pass', 2);

INSERT INTO public.app_platform(name, description, created_at, updated_at) VALUES ('ROCKIOT', 'ROCKIOT platform', NOW(), NOW());

INSERT INTO public.app_platformattribute(name, value, description, created_at, updated_at, platform_id) VALUES ('INGEST_INTERVAL', '60', 'Ingest interval for sensor devices', NOW(), NOW(), 1);

INSERT INTO public.app_platformattribute(name, value, description, created_at, updated_at, platform_id) VALUES ('SSL_ENABLED', 'false', 'Indicates if devices should communicate with platform using SSL', NOW(), NOW(), 1);

INSERT INTO public.auth_group(name) VALUES ('RESEARCHER');

INSERT INTO public.auth_group(name) VALUES ('DEVICE_ADMIN');

INSERT INTO public.auth_group(name) VALUES ('DEVICE_INSTALLER');

INSERT INTO public.auth_group(name) VALUES ('PLATFORM_ADMIN');

INSERT INTO public.auth_group(name) VALUES ('CONNECTED_API_USER');

INSERT INTO public.auth_group(name) VALUES ('PUBLIC_API_USER');