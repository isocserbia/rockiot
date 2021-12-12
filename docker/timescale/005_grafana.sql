CREATE USER grafanareader WITH PASSWORD 'grafanareader';
GRANT CONNECT ON DATABASE rock_iot TO grafanareader;
GRANT USAGE ON SCHEMA public TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO grafanareader;

CREATE USER prometheus WITH PASSWORD 'prometheus';
GRANT CONNECT ON DATABASE postgres TO prometheus;
GRANT CONNECT ON DATABASE rock_iot TO prometheus;
GRANT USAGE ON SCHEMA public TO prometheus;
GRANT USAGE ON SCHEMA pg_catalog TO prometheus;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO prometheus;
GRANT SELECT ON ALL TABLES IN SCHEMA pg_catalog TO prometheus;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO prometheus;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA pg_catalog TO prometheus;