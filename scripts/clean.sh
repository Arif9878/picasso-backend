#!/usr/bin/env bash

## Remove all containers related to metricbeat
CONTAINERS=`docker ps | grep gateway | awk '{print $1}'`
[ ! -z "${CONTAINERS}" ] && docker rm -f ${CONTAINERS}
echo "All containers removed !"
docker network rm gateway 2>&1 > /dev/null || true
exit 0
