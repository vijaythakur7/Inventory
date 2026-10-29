import requests
from requests.exceptions import Timeout, ConnectionError
from config.db_config import Config


class UserServiceUnavailable(Exception):
    pass


def get_current_user(token):

    url = f"{Config.USER_SERVICE_URL}/api/users/profile"

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Service-Key": Config.USER_SERVICE_KEY
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        return response

    except Timeout as exc:
        raise UserServiceUnavailable(
            "User service request timed out"
        ) from exc

    except ConnectionError as exc:
        raise UserServiceUnavailable(
            "User service is unavailable"
        ) from exc