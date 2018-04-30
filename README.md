# pg_notify_webhook

`pg_notify_webhook` is a utility for PostgreSQL which calls a webhook with row changes as JSON whenever an INSERT, UPDATE or DELETE event occurs on a particular table. It comprises of a PostgreSQL trigger function and a C binary called `skor` that listens to database notifications and invokes the webhook with a JSON payload.

## Usage

### Set up the trigger

Create the trigger and add it to the tables for which you want to get the change events using the init script.

```bash
$ ./init.sh table1 table2 | psql -h localhost -p 5432 -U postgres -d postgres --
```

### Run Skor:
A pre-built Docker image with the `skor` binary is available at `sidmutha/hasura-skor`.

Run it as:

```bash
$ docker run \
    -e DBNAME="postgres" \
    -e PGUSER="postgres" \
    -e PGPASS="''" \
    -e PGHOST="localhost" \
    -e PGPORT=5432 \
    -e WEBHOOKURL="http://localhost:5000/"
    --net host \
    -it sidmutha/hasura-skor:v0.1.1
```

Currently the program only listens on one channel called `skor`. All events have to be published to this channel. These events are forwarded to the given webhook url. The events are *not* redelivered if they fail once.


## Examples

### INSERT

Query:
```sql
INSERT INTO test_table(name) VALUES ('abc1');
```

JSON webhook payload:

```json
{"data": {"id": 1, "name": "abc1"}, "table": "test_table", "op": "INSERT"}
```

### UPDATE

Query:
```sql
UPDATE test_table SET name = 'pqr1' WHERE id = 1;
```

JSON webhook payload:

```json
{"data": {"id": 1, "name": "pqr1"}, "table": "test_table", "op": "UPDATE"}
```

### DELETE

Query:
```sql
DELETE FROM test_table WHERE id = 1;
```

JSON webhook payload:

```json
{"data": {"id": 1, "name": "pqr1"}, "table": "test_table", "op": "DELETE"}
```

## Deploying Skor on Hasura

The pre-built Docker image with the `skor` binary is available at `sidmutha/hasura-skor` and can be deployed as a microservice with the sample `k8s.yaml` in this repo.
The webhook can be another microservice that exposes an endpoint.

To learn more on deploying microservices on Hasura you may check out the [documentation](https://docs.hasura.io/0.15/manual/microservices/index.html).


## Build:

Run:

```bash
$ make
```


## Test

The test runs `skor` and a python-flask server for the webhook. Make sure you have installed python-flask before running the test.

Run the test (present in the root directory) as:

```bash
$ python test.py
```