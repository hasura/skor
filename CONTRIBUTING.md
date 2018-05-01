# Code of Conduct
This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. 

# Development Environment
Make sure you have the following installed:
- PostgreSQL 9+
- `gcc` 
- libcurl (`libcurl4-openssl-dev`) 
- libppq (`libpq-dev`)

# Build
Build the project using `make`:

```bash
$ make
```

# Run
Run the application with the arguments specifying database and webhook parameters: 

```bash
$ ./build/skor 'host=localhost port=5432 dbname=postgres user=postgres password=' http://localhost:5000
```

# Tests
Tests have been written using Python 3. The webhook is a `python-flask` server. 

To run tests make sure you have Postgres running at `localhost:5432` and the database doesn't already have a table named `test_table`.

You can modify the Postgres credentials in the `test.py` file.

Run the tests from the root directory as:

```bash
$ python test.py
```