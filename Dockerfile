FROM hasura/haskell-docker-packager:1.1
RUN apt-get update && apt-get install -y pkgconf libcurl4-openssl-dev libpq-dev \
 && rm -rf /var/lib/apt/lists/*

ENV DBNAME "postgres"
ENV PGUSER "postgres"
ENV PGPASS "''" 
ENV PGHOST "localhost"
ENV PGPORT 5432
ENV WEBHOOKURL "http://localhost:5000"

COPY ./src /skor/src
COPY Makefile /skor/
WORKDIR /skor

RUN make

CMD "./build/skor" "host=${PGHOST} port=${PGPORT} dbname=${DBNAME} user=${PGUSER} password=${PGPASS}" ${WEBHOOKURL}
