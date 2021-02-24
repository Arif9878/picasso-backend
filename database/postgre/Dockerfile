FROM postgres:12-alpine
COPY datamaster.sql .
RUN chmod -R 777 datamaster.sql
COPY init-user-db.sh /docker-entrypoint-initdb.d/init-user-db.sh