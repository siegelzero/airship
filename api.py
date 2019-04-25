import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime as dt
from http import HTTPStatus
from typing import Dict
from uuid import UUID

from flask import Flask, jsonify, request
from flask.wrappers import Response


app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


# Load the username:password values from the json file.
# This loads once when the service is started; not dynamically!
with open("./credentials.json") as f:
    credentials = json.load(f)


# fake db schema for Contact
@dataclass
class Contact:
    name: str = ''
    email: str = ''
    phone: str = ''

    created_by: str = ''
    created_time: str = field(default_factory=dt.utcnow)

    last_modified_by: str = ''
    last_modified_time: str = field(default_factory=dt.utcnow)


# In memory storage maintained as a dict.
db: Dict[UUID, Contact] = {}


# Let's define some Exceptions. First basic 404 response.
@app.errorhandler(HTTPStatus.NOT_FOUND)
def handle_not_found(e):
    response = jsonify({'error': {
        'status': HTTPStatus.NOT_FOUND,
        'detail': 'Invalid resource URI',
        }})
    response.status_code = 404
    return response


# 401 for invalid username/password
class UnauthorizedError(Exception):
    pass


@app.errorhandler(UnauthorizedError)
def handle_unauthorized(e):
    response = jsonify({'error': {
        'status': HTTPStatus.UNAUTHORIZED,
        'detail': e.args[0]
        }})
    response.status_code = 401
    return response


# 400 for client error
class UserError(Exception):
    pass


@app.errorhandler(UserError)
def handle_user(e):
    response = jsonify({'error': {
        'status': HTTPStatus.BAD_REQUEST,
        'detail': e.args[0]
        }})
    response.status_code = 400
    return response


# Now some common methods.
def verify_authorization(request):
    """Simple username/password verification."""
    username = request.authorization.get("username", "")
    password = request.authorization.get("password", "")
    if username not in credentials or password != credentials[username]:
        raise UnauthorizedError("Invalid username/password.")


def format_response(rows) -> Response:
    """Method to format row data into JSON output. This is simple but
    extensible, in case we need to add paging data to the response."""
    return jsonify({'data': rows})


def get_row_by_id(pk: UUID) -> Response:
    """Returns JSON output for the Contact with primary key pk."""
    # Resource not found, so raise 404.
    if pk not in db:
        raise UserError(f"Contact id '{pk}' not found")
    return format_response([{'id': pk, **db[pk].__dict__}])


# Now the API methods.
@app.route("/contacts/", methods=['GET'])
def get__multiple() -> Response:
    """Get multiple records from the db. If params are specified in the
    request, then the records that match the params will be returned.
    Otherwise, all records are returned."""
    rows = ({'id': pk, **row.__dict__} for (pk, row) in db.items())
    params = request.args
    rows = filter(lambda r: all(r[k] == params[k] for k in params), rows)

    # Ensure consistent ordering of results.
    return jsonify({'data': sorted(rows, key=lambda r: r['created_time'])})


@app.route("/contacts/<uuid:pk>", methods=['GET'])
def get__single(pk: UUID) -> Response:
    """Get single record matching the given uuid."""
    return get_row_by_id(pk)


@app.route("/contacts/", methods=['POST'])
def post() -> Response:
    """POST new record to the db."""
    verify_authorization(request)
    pk = uuid.uuid4()
    try:
        # Create a new Contact and take note of user.
        db[pk] = Contact(**request.json)
        setattr(db[pk], 'created_by', request.authorization.username)
        setattr(db[pk], 'last_modified_by', request.authorization.username)
    except TypeError:
        raise UserError("Invalid JSON")
    return get_row_by_id(pk)


@app.route("/contacts/<uuid:pk>", methods=['DELETE'])
def delete(pk: UUID) -> Response:
    """Delete record from the db."""
    verify_authorization(request)
    try:
        db.pop(pk)
    except KeyError:
        raise UserError(f"Invalid id '{pk}'")
    return jsonify({})


@app.route("/contacts/<uuid:pk>", methods=['PATCH'])
def patch(pk: UUID):
    """Delete record from the db."""
    verify_authorization(request)
    if pk not in db:
        raise UserError(f"Invalid id '{pk}'")

    # Only update allowed fields.
    update = request.json
    for key in update.keys() & db[pk].__dict__.keys():
        setattr(db[pk], key, update[key])

    # Record the user and time of modification.
    setattr(db[pk], 'last_modified_by', request.authorization.username)
    setattr(db[pk], 'last_modified_time', dt.utcnow())
    return get_row_by_id(pk)


if __name__ == "__main__":
    app.run()
