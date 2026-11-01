
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    # Database configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Encode password to handle special characters
    encoded_password = quote_plus(DB_PASSWORD)

    # SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{encoded_password}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
    USER_SERVICE_KEY = os.getenv("USER_SERVICE_KEY")

    @classmethod
    def validate(cls):

        required_settings = {
            "SECRET_KEY": cls.SECRET_KEY,
            "DB_NAME": cls.DB_NAME,
            "DB_USER": cls.DB_USER,
            "USER_SERVICE_URL": cls.USER_SERVICE_URL,
            "USER_SERVICE_KEY": cls.USER_SERVICE_KEY,
        }

        missing_settings = [
            key
            for key, value in required_settings.items()
            if not value
        ]

        if missing_settings:
            raise RuntimeError(
                "Missing required environment variables: "
                + ", ".join(missing_settings)
            )
