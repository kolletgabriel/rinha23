from datetime import date
from typing import Annotated

from flask import Flask, request
from pydantic import BaseModel, ValidationError, StringConstraints, Field
from psycopg2 import connect
from psycopg2.errors import UniqueViolation


DSN = {
    'host': 'db',
    'dbname': 'postgres',
    'user': 'postgres',
    'password':'rinha'
}

INSERT = """INSERT INTO users (nickname,fullname,dob,stack)
            VALUES (%s,%s,%s,%s)
            RETURNING id"""


type String32 = Annotated[str, StringConstraints(max_length=32)]
type String100 = Annotated[str, StringConstraints(max_length=100)]
type StackArray = Annotated[list[String32], Field(min_length=1)]

class UserModel(BaseModel):
    nickname: String32
    fullname: String100
    dob: date
    stack: StackArray | None = None

    def to_tuple(self) -> tuple:
        return (self.nickname, self.fullname, self.dob, self.stack)


app = Flask(__name__)
app.register_error_handler(400, lambda _: ('',400))
app.register_error_handler(404, lambda _: ('',404))
app.register_error_handler(ValidationError, lambda _: ('',422))
app.register_error_handler(UniqueViolation, lambda _: ('',422))


@app.route('/')
def healthcheck():
    return { 'status': 'ok' }


@app.route('/users', methods=['POST'])
def add_user():
    new_user = UserModel(**request.json)

    with connect(**DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(INSERT, new_user.to_tuple())
            return ('', 201, {'Location': f'/users/{cur.fetchone()[0]}'})
