from flask import Flask, request, json
from psycopg2.errors import UniqueViolation
from psycopg2.extensions import TRANSACTION_STATUS_INERROR
from pydantic import ValidationError

import schema
import db


conn, cur = db.setup_conn()

json.provider.DefaultJSONProvider.sort_keys = False
app = Flask(__name__)

app.register_error_handler(400, lambda _: ('',400))
app.register_error_handler(404, lambda _: ('',404))
app.register_error_handler(ValidationError, lambda _: ('',422))
app.register_error_handler(UniqueViolation, lambda _: ('',422))


@app.teardown_request
def commit_or_rollback(_):
    if conn.info.transaction_status is TRANSACTION_STATUS_INERROR:
        conn.rollback()
        return
    conn.commit()


@app.route('/users', methods=['POST'])
def add_user():
    new_user = schema.UserModel(**request.json)
    cur.execute(db.INSERT_QUERY, new_user.to_tuple())
    return ('', 201, {'Location': f'/users/{cur.fetchone()['id']}'})


@app.route('/users/<user_id>')
def get_user(user_id):
    cur.execute(db.SELECT_QUERY, (user_id,))
    result = cur.fetchone()
    if not result:
        return ('', 404)
    return result


@app.route('/users')
def search_users():
    query = request.args.get('q')
    if not query or query == '\x00':
        return ('', 400)
    cur.execute(db.SEARCH_QUERY, (f'%{query}%',))
    return cur.fetchall()


@app.route('/users-count')
def count_users():
    cur.execute(db.COUNT_QUERY)
    return cur.fetchone()['result']
