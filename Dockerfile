FROM debian:jessie-20180426 as skor-builder
MAINTAINER vamshi@hasura.io

RUN apt-get update && apt-get install -y build-essential pkgconf libcurl4-openssl-dev libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY ./src /skor/src
COPY Makefile /skor/
WORKDIR /skor
RUN make

FROM debian:jessie-20180426

RUN apt-get update && apt-get install -y libcurl3 libpq5 \
 && rm -rf /var/lib/apt/lists/*

ENV DBNAME "postgres"
ENV PGUSER "postgres"
ENV PGPASS "''"
ENV PGHOST "localhost"
ENV PGPORT 5432
ENV WEBHOOKURL "http://localhost:5000"
ENV LOG_LEVEL "2"

COPY --from=skor-builder /skor/build/skor /usr/bin/skor
COPY Makefile /skor/
WORKDIR /skor

CMD "skor" "host=${PGHOST} port=${PGPORT} dbname=${DBNAME} user=${PGUSER} password=${PGPASS}" "${WEBHOOKURL}" "${LOG_LEVEL}"
