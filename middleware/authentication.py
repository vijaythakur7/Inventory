
from functools import wraps

from flask import request, jsonify, g

from clients.user_client import (
    get_current_user,
    UserServiceUnavailable
)


def authenticate_request():

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, (
            jsonify({
                "message": "Valid Bearer token is required"
            }),
            401
        )

    token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return None, (
            jsonify({
                "message": "Valid Bearer token is required"
            }),
            401
        )

    try:
        response = get_current_user(token)

    except UserServiceUnavailable as exc:
        return None, (
            jsonify({
                "message": str(exc)
            }),
            503
        )

    if not response.ok:
        return None, (
            jsonify({
                "message": "Authentication failed"
            }),
            response.status_code
        )

    try:
        user_data = response.json()

    except ValueError:
        return None, (
            jsonify({
                "message": "User Service returned invalid JSON"
            }),
            502
        )

    user_id = user_data.get("id")

    if user_id is None:
        return None, (
            jsonify({
                "message": "User ID missing from User Service response"
            }),
            502
        )

    return user_id, None


def require_authentication(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        user_id, error_response = authenticate_request()

        if error_response:
            return error_response

        g.user_id = user_id

        return function(*args, **kwargs)

    return decorated_function
