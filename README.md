# pg_notify_webhook

`pg_notify_webhook` is a utility for PostgreSQL which calls a webhook with row changes as JSON whenever an INSERT, UPDATE or DELETE event occurs on a particular table. 

## Build:

```bash
$ make
```
## Usage

### Set up the trigger

Create the trigger and add it to the tables for which you want to get the change events using the init script.

```bash
$ ./init.sh table1 table2 | psql -h localhost -p 5432 -U postgres -d postgres --
```

### Run the binary:

```bash
$ ./build/skor 'host=localhost port=5432 dbname=postgres user=postgres password=' http://localhost:5000
```

Currently the utility only listens on one channel called `skor`. All events have to be published to this channel. These events are forwarded to the given webhook url. The events are *not* redelivered if they fail once.


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


## Test

Run the test (present in the root directory):

```bash
$ python test.py
```