CREATE USER grafanareader WITH PASSWORD 'grafanareader';
GRANT CONNECT ON DATABASE rock_iot TO grafanareader;
GRANT USAGE ON SCHEMA public TO grafanareader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafanareader;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO grafanareader;
