#!/bin/bash
i=0
while [ $i -ne 200 ]
do
    i=$(($i+1))
    PGPASSWORD=postgres psql -h localhost -U postgres -d rock_iot -P pager=on --set AUTOCOMMIT=on -t -c "INSERT INTO public.app_device(name, description, device_id, created_at, updated_at, status, mode, metadata, location, device_pass, facility_id) VALUES('Device 999${i}', '', 'device999${i}', '2021-08-09 19:03:47.082159+00', '2021-08-09 19:24:34.170107+00', 'REGISTERED', 'DEFAULT', '{}', '0101000020E61000008111F5FFFF4722401DCFE914A7AA2540', 'device999${i}pass', 1);"
done
