
from functools import wraps

from flask import g, request

from clients.user_client import (
    get_current_user,
    UserServiceUnavailable
)

from utils.response import error_response


def authenticate_request():

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, error_response(
            "Valid Bearer token is required",
            401
        )

    token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return None, error_response(
            "Valid Bearer token is required",
            401
        )

    try:
        response = get_current_user(token)

    except UserServiceUnavailable as exc:
        return None, error_response(
            str(exc),
            503
        )

    if not response.ok:
        return None, error_response(
            "Authentication failed",
            response.status_code
        )

    try:
        user_data = response.json()

    except ValueError:
        return None, error_response(
            "User Service returned invalid JSON",
            502
        )

    user_id = user_data.get("id")

    if user_id is None:
        return None, error_response(
            "User ID missing from User Service response",
            502
        )

    return user_id, None


def require_authentication(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        user_id, error_response_result = authenticate_request()

        if error_response_result:
            return error_response_result

        g.user_id = user_id

        return function(*args, **kwargs)

    return decorated_function
