# skor

Build:

```bash
make
```

Run:

```bash
./build/skor 'host=localhost port=7432 dbname=chinook user=admin password=' http://localhost:8080
```

Currently skor only listens on one channel called `skor`. All events have to be published to this channel. These events are forwarded to the given webhook url. The events are *not* redelivered if they fail once.

## Getting events from table:

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

For each table that you want to get events for, you can add this trigger;

``` bash
CREATE TRIGGER notify_skor AFTER INSERT OR DELETE OR UPDATE ON <table-name> FOR EACH ROW EXECUTE PROCEDURE notify_skor();
```
