import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

from config.db_config import Config


class UserServiceUnavailable(Exception):
    pass


def create_user_service_session():

    session = requests.Session()

    retry_strategy = Retry(
        total=Config.USER_SERVICE_RETRIES,
        connect=Config.USER_SERVICE_RETRIES,
        read=Config.USER_SERVICE_RETRIES,
        status=Config.USER_SERVICE_RETRIES,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

def get_current_user(token):

    url = f"{Config.USER_SERVICE_URL}/api/users/profile"

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Service-Key": Config.USER_SERVICE_KEY
    }

    session = create_user_service_session()

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=Config.USER_SERVICE_TIMEOUT
        )

        return response

    except RequestException as exc:
        raise UserServiceUnavailable(
            "User service request timed out"
        ) from exc

    finally:
        session.close()