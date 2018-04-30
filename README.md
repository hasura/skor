# pg_notify_webhook

`pg_notify_webhook` is a utility for PostgreSQL which calls a webhook with row changes as JSON whenever an INSERT, UPDATE, DELETE event occurs on a particular table. 

## Build:

```bash
$ make
```
## Usage

### Set up the trigger

```sql

CREATE FUNCTION notify_skor() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  DECLARE
    cur_rec record;
    BEGIN
      IF (TG_OP = 'DELETE') THEN
        cur_rec = OLD;
      ELSE
        cur_rec = NEW;
      END IF;
      PERFORM pg_notify('skor', json_build_object(
                    'data',  row_to_json(cur_rec),
                    'table', TG_TABLE_NAME,
                    'op',    TG_OP
              )::text);
      RETURN cur_rec;
    END;
$$;

```

For each table that you want to get events for, create this trigger;

``` bash
CREATE TRIGGER notify_skor AFTER INSERT OR DELETE OR UPDATE ON <table-name> FOR EACH ROW EXECUTE PROCEDURE notify_skor();
```


### Run the binary:

```bash
$ ./build/pg_notify_webhook 'host=localhost port=5432 dbname=postgres user=postgres password=' http://localhost:8080
```

Currently the utility only listens on one channel called `skor`. All events have to be published to this channel. These events are forwarded to the given webhook url. The events are *not* redelivered if they fail once.


## Examples

### INSERT

Query:
```sql
INSERT INTO test_table(name) VALUES ('abc1');
```

JSON output:

```json
{"data": {"id": 1, "name": "abc1"}, "table": "test_table", "op": "INSERT"}
```

### UPDATE

Query:
```sql
UPDATE test_table SET name = 'pqr1' WHERE id = 1;
```

JSON output:

```json
{"data": {"id": 1, "name": "pqr1"}, "table": "test_table", "op": "UPDATE"}
```

### DELETE

Query:
```sql
DELETE FROM test_table WHERE id = 1;
```

JSON output:

```json
{"data": {"id": 1, "name": "pqr1"}, "table": "test_table", "op": "DELETE"}
```


## Test

Run the test (present in the root directory):

```bash
$ python test.py
```