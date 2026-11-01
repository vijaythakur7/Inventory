
class TestingConfig:

    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WTF_CSRF_ENABLED = False

    JWT_SECRET_KEY = "testing-secret-key"
