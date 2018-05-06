#!/usr/bin/env sh

set -e

psql -h 127.0.0.1 -p 5432 -d skor_test -U admin --single-transaction -f schema.sql
../gen-triggers.py triggers.json | psql -h 127.0.0.1 -p 5432 -d skor_test -U admin --single-transaction --
./test.py
