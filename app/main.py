from flask import Flask, request, json
from psycopg2.errors import UniqueViolation, InvalidTextRepresentation
from psycopg2.extensions import TRANSACTION_STATUS_INERROR
from pydantic import ValidationError

import schema
import db


CONN, CUR = db.setup_conn()


json.provider.DefaultJSONProvider.sort_keys = False
app = Flask(__name__)

app.register_error_handler(400, lambda _: ('',400))
app.register_error_handler(InvalidTextRepresentation, lambda _: ('',400))
app.register_error_handler(404, lambda _: ('',404))
app.register_error_handler(UniqueViolation, lambda _: ('',422))
app.register_error_handler(500, lambda _: ('',500))  # shut up

@app.errorhandler(ValidationError)
def handle_pydantic_errors(exception):
    e = exception.errors()
    for err in e:
        if err['type'].endswith('_type') or err['type'].startswith('date_'):
            if err['input'] is not None:
                return ('', 400)
            return ('', 422)
    return ('', 422)


@app.route('/users', methods=['POST'])
def add_user():
    new_user = schema.UserModel(**request.json)
    CUR.execute(db.INSERT_QUERY, new_user.to_tuple())
    return ('', 201, {'Location': f'/users/{CUR.fetchone()['id']}'})


@app.route('/users/<user_id>')
def get_user(user_id):
    CUR.execute(db.SELECT_QUERY, (user_id,))
    result = CUR.fetchone()
    if not result:
        return ('', 404)
    return result


@app.route('/users')
def search_users():
    query = request.args.get('q')
    if not query or query == '\x00':
        return ('', 400)
    CUR.execute(db.SEARCH_QUERY, (f'%{query}%',))
    return CUR.fetchall()


@app.route('/users-count')
def count_users():
    CUR.execute(db.COUNT_QUERY)
    return CUR.fetchone()['result']


@app.teardown_request
def commit_or_rollback(_):
    if CONN.info.transaction_status is TRANSACTION_STATUS_INERROR:
        CONN.rollback()
        return
    CONN.commit()
