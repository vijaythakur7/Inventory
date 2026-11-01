
from types import SimpleNamespace


def test_missing_authorization_header(client):

    response = client.get("/api/categories/user")

    assert response.status_code == 401

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Valid Bearer token is required"


def test_invalid_token(client, monkeypatch):

    def mock_get_current_user(token):

        return SimpleNamespace(
            ok=False,
            status_code=401
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.get(
        "/api/categories/user",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401

    response_data = response.get_json()

    assert response_data["success"] is False
    assert response_data["message"] == "Authentication failed"


def test_valid_token(client, monkeypatch):

    def mock_get_current_user(token):

        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {
                "id": 101,
                "name": "Test User",
                "email": "test@example.com"
            }
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )

    response = client.get(
        "/api/categories/user",
        headers={
            "Authorization": "Bearer valid-test-token"
        }
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["data"]["user_id"] == 101
