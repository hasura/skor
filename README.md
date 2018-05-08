# Skor

`skor` is a utility for Postgres which calls a webhook with row changes as JSON whenever an INSERT, UPDATE or DELETE event occurs on a particular table.
You can drop the docker image next to your Postgres database instance and configure a webhook that will be called.

It works using a `pg_notify` trigger function and a tiny C program `skor` that listens to the notifications and calls the configured webhook with a JSON payload.

## When to use
+ When you want to trigger an action in an external application when a table row is modified.
+ When you want a lightweight notification system for changes in the database.
+ When you want to send the changes to a message queue such as AMQP, Kafka etc.

## How it works
A PostgreSQL stored procedure is set up as a trigger on the required table(s). This trigger uses PostgreSQL's LISTEN and NOTIFY to publish change events as JSON to a notification channel. `Skor` watches this channel for messages and when a message is received, it makes an HTTP POST call to the webhook with the JSON payload. The webhook can then decide to take an action on this.

![Skor Architecture Diagram](assets/skor-arch.png "Skor Architecture")


## Caveats
+ Events are only captured when skor is running.
+ If a call to the webhook fails, it is **not** retried.

## Getting started

### 1) Set up the triggers:

We need to setup triggers on the tables that we we are interested in. Create a `triggers.json` file (see [sample.triggers.json](sample.triggers.json)) with the required tables and events.

Note: This command requires `python3`.

```bash
$ ./gen-triggers.py triggers.json | psql -h localhost -p 5432 -U postgres -d postgres --single-transaction --
```

### 2) Run Skor:

Run the skor Docker image (that has the `skor` binary baked in):

```bash
$ docker run \
    -e DBNAME="postgres" \
    -e PGUSER="postgres" \
    -e PGPASS="''" \
    -e PGHOST="localhost" \
    -e PGPORT=5432 \
    -e WEBHOOKURL="http://localhost:5000/" \
    --net host \
    -it hasura/skor:v0.1.1
```

Make sure you use the appropriate database parameters and webhook URL above.

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

## Uninstalling

To remove the skor related functions and triggers that were added to Postgres, run this in psql:

```sql
DO $$DECLARE r record;
BEGIN
    FOR r IN SELECT routine_schema, routine_name FROM information_schema.routines
             WHERE routine_name LIKE 'notify_skor%'
    LOOP
        EXECUTE 'DROP FUNCTION ' || quote_ident(r.routine_schema) || '.' || quote_ident(r.routine_name) || ' CASCADE';
    END LOOP;
END$$;
```

## Deploying Skor on Hasura

The pre-built Docker image with the `skor` binary is available at `hasura/skor` and can be deployed as a microservice with the sample `k8s.yaml` in this repo.
The webhook can be another microservice that exposes an endpoint.

To learn more on deploying microservices on Hasura you may check out the [documentation](https://docs.hasura.io/0.15/manual/microservices/index.html).


## Build Skor:

### Requirements:

+ PostgreSQL 9+
+ `gcc`
+ libcurl (`libcurl4-openssl-dev`)
+ libppq (`libpq-dev`)


### Build:

```bash
$ make
```
### Run:

```bash
$ ./build/skor 'host=localhost port=5432 dbname=postgres user=postgres password=' http://localhost:5000
```

## Test

1. Install the requirements specified in `tests/requirements.txt`
2. The tests assume that you have a local postgres instance at `localhost:5432` and a database called `skor_test` which can be accessed by an `admin` user.
3. Run skor on this database with the webhook url set to `http://localhost:5000`
4. run `run_tests.sh` script in the `tests` directory.

## Contributing
Contributions are welcome!

Please check out the [contributing guide](CONTRIBUTING.md) to learn about setting up the development environment and building the project. Also look at the [issues](https://github.com/hasura/skor/issues) page and help us in improving Skor!
