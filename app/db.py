from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import string_types


# Disable conversions for date and longint, repsectively:
string_types.pop(1082)
string_types.pop(20)


DSN = 'host=db dbname=postgres user=postgres password=rinha'
_connection = _cursor = None

def close_conn() -> None:
    global _connection, _cursor
    if _cursor and not _cursor.closed:
        _cursor.close()
        if _connection and not _connection.closed:
            _connection.close()
    _connection = _cursor = None

def setup_conn() -> tuple:
    global _connection, _cursor
    if not _connection or _connection.closed:
        _connection = connect(DSN, cursor_factory=RealDictCursor)
        _cursor = _connection.cursor()
    return (_connection, _cursor)


INSERT_QUERY = """INSERT INTO users (nickname,fullname,dob,stack)
                    VALUES (%s,%s,%s,%s)
                    RETURNING id;"""

SELECT_QUERY = """SELECT * FROM users WHERE id = %s;"""

COUNT_QUERY = """SELECT count(*) as result FROM users;"""

SEARCH_QUERY = """SELECT * FROM users
                    WHERE concat_cols(nickname,fullname,stack) ILIKE %s
                    LIMIT 50;"""
