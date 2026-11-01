
def test_app_creation(app):
    assert app is not None
    assert app.config["TESTING"] is True


def test_client_creation(client):
    assert client is not None
