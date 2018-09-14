# Skor

## New and improved version of Skor is now part of [Hasura GraphQL Engine](https://github.com/hasura/graphql-engine)

A few months ago, we built the open source [GraphQL Engine](https://github.com/hasura/graphql-engine) that gives you instant GraphQL APIs over any Postgres database. We have added all of Skor's existing features and even more to make it production ready:

 1) Reliable: We capture every relevant action on the database as an event, even when Hasura is down! The events are delivered to your webhook as soon as possible with an atleast-once guarantee.

2) Scalable: What more, it even scales horizontally. If you are processing millions of events, just add more instances of GraphQL engine.

3) Use with Serverless: If you are using Skor, then avoid the pain of managing your webhook by moving to Serverless infrastructure. Check out these blog posts to get started

**Use [Hasura GraphQL Engine](https://github.com/hasura/graphql-engine) for production use cases** 

---

`skor` is a utility for Postgres which calls a webhook with row changes as JSON whenever an INSERT, UPDATE or DELETE event occurs on a particular table.
You can drop the docker image next to your Postgres database instance and configure a webhook that will be called.

It works using a `pg_notify` trigger function and a tiny C program `skor` that listens to the notifications and calls the configured webhook with a JSON payload.

## When to use
- When you want to trigger an action in an external application when a table row is modified.
- When you want a lightweight notification system for changes in the database.
- When you want to send the changes to a message queue such as AMQP, Kafka etc.

## How it works
A PostgreSQL stored procedure is set up as a trigger on the required table(s). This trigger uses PostgreSQL's LISTEN and NOTIFY to publish change events as JSON to a notification channel. `Skor` watches this channel for messages and when a message is received, it makes an HTTP POST call to the webhook with the JSON payload. The webhook can then decide to take an action on this. Webhooks are retried upto 5 times with linear backoff in multiples of 100ms.

![Skor Architecture Diagram](assets/skor-arch.png "Skor Architecture")


## Caveats
- Events are only captured when skor is running.
- If a call to the webhook fails, it is **not** retried.

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

- PostgreSQL 9+
- `gcc`
- libcurl (`libcurl4-openssl-dev`)
- libppq (`libpq-dev`)


### Build:

```bash
$ make
```
### Run:

```bash
$ ./build/skor 'host=localhost port=5432 dbname=postgres user=postgres password=' http://localhost:5000
```

## Test

Steps to execute the tests:
1. Build `skor` (instructions above :top:), ensure there is a running postgres instance to test against
2. Define PGUSER, PGPASS, PGHOST and PGPORT env vars
3. Invoke `run_tests.sh` from the `tests` dir

The `run_tests.sh` script does the following:
1. Installs the requirements specified in `tests/requirements.txt` (make sure you are in a virtualenv before invoking)
2. (Re)Creates a database `skor_test` and adds the necessary tables, runs skor etc
3. Makes schema changes to the tables and makes sure `skor` gets them all right
4. Tears down `skor`, deletes the `skor_test` database

## Contributing
Contributions are welcome!

Please check out the [contributing guide](CONTRIBUTING.md) to learn about setting up the development environment and building the project. Also look at the [issues](https://github.com/hasura/skor/issues) page and help us in improving Skor!
