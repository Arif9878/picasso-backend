#!/bin/bash

set -e
set -u

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER $POSTGRESQL_USER WITH PASSWORD '$POSTGRESQL_PASSWORD';
    ALTER ROLE $POSTGRESQL_USER SET client_encoding TO 'utf8';
    ALTER ROLE $POSTGRESQL_USER SET default_transaction_isolation TO 'read committed';
    ALTER ROLE $POSTGRESQL_USER SET timezone TO '$POSTGRESQL_TIMEZONE';
    ALTER USER $POSTGRESQL_USER WITH SUPERUSER;
EOSQL

function create_user_and_database() {
	local database=$1
	echo "  Creating user and database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $POSTGRESQL_USER;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
	for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
		create_user_and_database $db
	done
	echo "Multiple databases created"
fi
# restore
psql --set ON_ERROR_STOP=on -U $POSTGRESQL_USER -d datamaster -1 -f datamaster.sql
rm datamaster.sql