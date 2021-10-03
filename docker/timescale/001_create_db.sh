#!/bin/bash


psql --username "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = 'rock_iot'" | grep -q 1 || psql --username "postgres" -tc "CREATE DATABASE rock_iot WITH OWNER postgres; GRANT ALL PRIVILEGES ON DATABASE rock_iot TO postgres;"