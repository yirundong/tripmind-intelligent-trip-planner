-- PostgreSQL database bootstrap for local TripMind demos.
-- Run with a superuser account:
--   psql -U postgres -f scripts/init_postgres.sql

DO
$$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'tripmind') THEN
        CREATE ROLE tripmind WITH LOGIN PASSWORD 'tripmind123';
    ELSE
        ALTER ROLE tripmind WITH LOGIN PASSWORD 'tripmind123';
    END IF;
END
$$;

SELECT 'CREATE DATABASE tripmind OWNER tripmind ENCODING ''UTF8'''
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'tripmind')
\gexec

GRANT ALL PRIVILEGES ON DATABASE tripmind TO tripmind;
