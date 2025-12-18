import time
import subprocess

import pytest
from psycopg2 import connect
from psycopg2.extras import execute_batch

from data.users import SAMPLE


DSN = 'host=localhost dbname=postgres user=postgres password=rinha'
QUERY = """INSERT INTO users VALUES (%s, %s, %s, %s, %s);"""


@pytest.fixture(scope='session', autouse=True)
def setup_compose():
    subprocess.run(['docker', 'compose', 'up', '-d'])
    time.sleep(3)  # wait
    yield
    subprocess.run(['docker', 'compose', 'down'])


@pytest.fixture
def populate_db():
    with connect(DSN) as conn:
        with conn.cursor() as cur:
            execute_batch(cur, QUERY, SAMPLE)


@pytest.fixture
def truncate():
    yield
    with connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""TRUNCATE TABLE users;""")
