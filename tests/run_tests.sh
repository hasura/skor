#!/usr/bin/env sh

set -e

if [ -z "${PGUSER}" ]
then
     echo "Undefined env var PGUSER (PGUSER, PGPASS, PGHOST, PGPORT and WEBHOOKURL all must be defined)"
     exit 1
elif [ -z "${PGPASS}" ]
then
     echo "Undefined env var PGPASS (PGUSER, PGPASS, PGHOST, PGPORT and WEBHOOKURL all must be defined)"
     exit 1
elif [ -z "${PGHOST}" ]
then
     echo "Undefined env var PGHOST (PGUSER, PGPASS, PGHOST, PGPORT and WEBHOOKURL all must be defined)"
     exit 1
elif [ -z "${PGPORT}" ]
then
     echo "Undefined env var PGPORT (PGUSER, PGPASS, PGHOST, PGPORT and WEBHOOKURL all must be defined)"
     exit 1
elif [ -z "${WEBHOOKURL}" ]
then
     echo "Undefined env var WEBHOOKURL (PGUSER, PGPASS, PGHOST, PGPORT and WEBHOOKURL all must be defined)"
     exit 1
fi

PS_ENDPOINT="postgres://${PGUSER}:${PGPASS}@${PGHOST}:${PGPORT}"

psql "$PS_ENDPOINT" -c "DROP DATABASE IF EXISTS skor_test;"
psql "$PS_ENDPOINT" -c "CREATE DATABASE skor_test;"
psql "$PS_ENDPOINT/skor_test" --single-transaction -f schema.sql
../gen-triggers.py triggers.json | psql "$PS_ENDPOINT/skor_test" --single-transaction --
../build/skor "$PS_ENDPOINT/skor_test" "${WEBHOOKURL}" &
./test.py
pkill -P $$
psql "$PS_ENDPOINT" -c "DROP DATABASE skor_test;"
