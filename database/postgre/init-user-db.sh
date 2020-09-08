#!/bin/bash
set -o errexit

create_user() {
  psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_USER" <<-EOSQL
    CREATE USER $POSTGRESQL_USER WITH PASSWORD $POSTGRESQL_PASSWORD;
    ALTER ROLE $POSTGRESQL_USER SET client_encoding TO 'utf8';
    ALTER ROLE $POSTGRESQL_USER SET default_transaction_isolation TO 'read committed';
    ALTER ROLE $POSTGRESQL_USER SET timezone TO $POSTGRESQL_TIMEZONE;
    ALTER ROLE $POSTGRESQL_USER WITH PASSWORD $POSTGRESQL_PASSWORD;
    ALTER USER $POSTGRESQL_USER WITH SUPERUSER;
EOSQL
}


create_database() {
	local database=$1
	echo "  Creating user and database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_USER" <<-EOSQL
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO "$POSTGRESQL_USER";
EOSQL
}

main() {
  create_user
  if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
  	echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
  	for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
  		create_database $db
  	done
  	echo "Multiple databases created"
  fi
}

main "$@"
