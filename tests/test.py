import subprocess, os
import time
import json

## set up test env

# using psql subprocess to execute sql instead of psycopg2 since it doesn't seem to fire the triggers
def psql(stmt):
  s = subprocess.Popen(["psql", "-hlocalhost", "-p5432", "-Upostgres", "-dpostgres", "-c {}".format(stmt)])
  s.wait()


print("starting webhook server")

# touch serverlog file before server starts 
# using this method since the Popen stdout doesn't give any output for the server
open("/tmp/serverlog","w").close()

# start server
server = subprocess.Popen(["python", "tests/server.py"], stdout=subprocess.PIPE)

# give time for the server to start
time.sleep(3)

create_function_stmt = """
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
"""
# create trigger function
psql(create_function_stmt)

# create test table
psql("CREATE TABLE test_table (id serial, name text);")

# create trigger on test_table
psql("CREATE TRIGGER notify_skor AFTER INSERT OR DELETE OR UPDATE ON test_table FOR EACH ROW EXECUTE PROCEDURE notify_skor();")

# start the skor binary
print("Starting skor")
skor = subprocess.Popen(["./build/skor", "host=localhost port=5432 dbname=postgres user=postgres password=", "http://localhost:5000"], stdout=subprocess.PIPE)


## set up complete

## begin testing
print("Begin testing")

expected_jsons = {
    'INSERT' : {'data': {'id': 1, 'name': 'abc1'}, 'op': 'INSERT', 'table': 'test_table'},
    'UPDATE' : {'data': {'id': 1, 'name': 'pqr1'}, 'op': 'UPDATE', 'table': 'test_table'},
    'DELETE' : {'data': {'id': 1, 'name': 'pqr1'}, 'op': 'DELETE', 'table': 'test_table'}
}

f = open("/tmp/serverlog", "r")

# function to verify outputs
def verify(op):
  line = None
  while not line:
    line = f.readline()
    
  print(line)
  
  # verify op
  expected = expected_jsons[op]

  out = json.loads(str(line))
  if expected == out:
      print("{} passed".format(op))
  else:
      print("{} failed".format(op))


# Insert
psql("INSERT INTO test_table(name) VALUES ('abc1');")
verify('INSERT')

# Update
psql("UPDATE test_table SET name = 'pqr1' WHERE id = 1")
verify('UPDATE')

# Delete
psql("DELETE FROM test_table WHERE id = 1")
verify('DELETE')

# time.sleep(3)



## teardown

print("Teardown test env")
f.close()
psql("DROP TABLE test_table;")
psql("DROP FUNCTION notify_skor;")
skor.terminate()
server.terminate()
os.remove("/tmp/serverlog")