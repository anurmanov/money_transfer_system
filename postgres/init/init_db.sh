#!bin/bash
cp /tmp/postgresql.conf /var/lib/postgresql/data
cp /tmp/pg_hba.conf /var/lib/postgresql/data
cd /docker-entrypoint-initdb.d
psql -c "create database money_transfer_system" postgres
psql -c "create database test_money_transfer_system" postgres
