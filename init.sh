#! /bin/bash

# script to initialize the trigger for given tables

# create function that calls pg_notify
echo \
'CREATE OR REPLACE FUNCTION notify_skor() RETURNS trigger 
    LANGUAGE plpgsql 
    AS $$ 
  DECLARE 
    cur_rec record; 
    BEGIN 
      IF (TG_OP = '"'DELETE'"') THEN 
        cur_rec = OLD; 
      ELSE 
        cur_rec = NEW; 
      END IF; 
      PERFORM pg_notify('"'skor'"', json_build_object( 
                    '"'data'"',  row_to_json(cur_rec), 
                    '"'table'"', TG_TABLE_NAME, 
                    '"'op'"',    TG_OP 
              )::text); 
      RETURN cur_rec; 
    END; 
$$;'


# add trigger to input tables
for table in "$@"
do  
    echo "DROP TRIGGER IF EXISTS notify_skor ON $table;"
    echo "CREATE TRIGGER notify_skor AFTER INSERT OR DELETE OR UPDATE ON $table FOR EACH ROW EXECUTE PROCEDURE notify_skor();"
done
