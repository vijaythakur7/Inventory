
import pytest
from types import SimpleNamespace

from extensions import db
from models.products_model import Product
from models.categories_model import Category
from models.stock_movements_model import StockMovement


# ============================================================
# TEST HELPERS
# ============================================================

def authenticate_as(monkeypatch, user_id=101):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {
                "id": user_id,
                "name": "Test User",
                "email": "test@example.com"
            }
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )


def auth_headers():
    return {
        "Authorization": "Bearer valid-test-token"
    }


def create_category(user_id=101):

    category = Category(
        name="Electronics",
        description="Electronic products",
        user_id=user_id
    )

    db.session.add(category)
    db.session.commit()

    return category


def create_product(
    user_id=101,
    quantity=20,
    minimum_stock=5
):

    category = create_category(user_id)

    product = Product(
        name="Laptop",
        sku=f"LAP-{user_id}",
        price=50000,
        quantity=quantity,
        minimum_stock=minimum_stock,
        category_id=category.id,
        user_id=user_id
    )

    db.session.add(product)
    db.session.commit()

    return product


# ============================================================
# STOCK IN TESTS
# ============================================================

def test_stock_in_success(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product(quantity=20)

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={
            "quantity": 10,
            "reason": "New stock received"
        },
        headers=auth_headers()
    )

    assert response.status_code == 201

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["message"] == "Stock added successfully"

    movement_data = response_data["data"]["movement"]

    assert movement_data["type"] == "IN"
    assert movement_data["quantity"] == 10
    assert movement_data["reason"] == "New stock received"

    updated_product = db.session.get(Product, product.id)

    assert updated_product.quantity == 30


def test_stock_in_creates_movement_record(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product(quantity=10)

    client.post(
        f"/api/products/{product.id}/stock-in",
        json={"quantity": 5},
        headers=auth_headers()
    )

    movement = StockMovement.query.filter_by(
        product_id=product.id,
        user_id=101,
        movement_type="IN"
    ).first()

    assert movement is not None
    assert movement.quantity == 5


def test_stock_in_without_quantity(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={"reason": "Received stock"},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Quantity is required"


# ============================================================
# STOCK OUT TESTS
# ============================================================

def test_stock_out_success(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product(quantity=20)

    response = client.post(
        f"/api/products/{product.id}/stock-out",
        json={
            "quantity": 5,
            "reason": "Customer purchase"
        },
        headers=auth_headers()
    )

    assert response.status_code == 201

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["message"] == "Stock removed successfully"

    movement_data = response_data["data"]["movement"]

    assert movement_data["type"] == "OUT"
    assert movement_data["quantity"] == 5

    updated_product = db.session.get(Product, product.id)

    assert updated_product.quantity == 15


def test_stock_out_creates_movement_record(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product(quantity=20)

    client.post(
        f"/api/products/{product.id}/stock-out",
        json={"quantity": 5},
        headers=auth_headers()
    )

    movement = StockMovement.query.filter_by(
        product_id=product.id,
        user_id=101,
        movement_type="OUT"
    ).first()

    assert movement is not None
    assert movement.quantity == 5


def test_stock_out_insufficient_stock(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product(quantity=5)

    response = client.post(
        f"/api/products/{product.id}/stock-out",
        json={"quantity": 10},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Insufficient stock"

    updated_product = db.session.get(Product, product.id)

    assert updated_product.quantity == 5

    assert StockMovement.query.filter_by(
        product_id=product.id
    ).count() == 0


# ============================================================
# QUANTITY VALIDATION TESTS
# ============================================================

@pytest.mark.parametrize(
    "quantity, expected_message",
    [
        (0, "Quantity must be greater than zero"),
        (-5, "Quantity must be greater than zero"),
        ("10", "Quantity must be an integer"),
        (10.5, "Quantity must be an integer"),
        (True, "Quantity must be an integer"),
    ]
)
def test_stock_in_invalid_quantity(
    client,
    monkeypatch,
    quantity,
    expected_message
):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={"quantity": quantity},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == expected_message


@pytest.mark.parametrize(
    "quantity, expected_message",
    [
        (0, "Quantity must be greater than zero"),
        (-2, "Quantity must be greater than zero"),
        ("five", "Quantity must be an integer"),
        (2.5, "Quantity must be an integer"),
        (False, "Quantity must be an integer"),
    ]
)
def test_stock_out_invalid_quantity(
    client,
    monkeypatch,
    quantity,
    expected_message
):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-out",
        json={"quantity": quantity},
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == expected_message


# ============================================================
# REASON VALIDATION TESTS
# ============================================================

def test_stock_in_with_empty_reason(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={
            "quantity": 5,
            "reason": "   "
        },
        headers=auth_headers()
    )

    assert response.status_code == 201
    assert response.get_json()["data"]["movement"]["reason"] is None


def test_stock_in_reason_not_string(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={
            "quantity": 5,
            "reason": 123
        },
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Reason must be a string"


def test_stock_in_reason_exceeds_max_length(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={
            "quantity": 5,
            "reason": "A" * 256
        },
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Reason cannot exceed 255 characters"
    )


# ============================================================
# PRODUCT OWNERSHIP TESTS
# ============================================================

def test_user_cannot_stock_in_another_users_product(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, user_id=202)

    product = create_product(user_id=101)

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={"quantity": 5},
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"

    updated_product = db.session.get(Product, product.id)

    assert updated_product.quantity == 20


def test_user_cannot_stock_out_another_users_product(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, user_id=202)

    product = create_product(user_id=101)

    response = client.post(
        f"/api/products/{product.id}/stock-out",
        json={"quantity": 5},
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"

    updated_product = db.session.get(Product, product.id)

    assert updated_product.quantity == 20


# ============================================================
# STOCK HISTORY TESTS
# ============================================================

def test_get_stock_history(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product(quantity=20)

    client.post(
        f"/api/products/{product.id}/stock-in",
        json={
            "quantity": 10,
            "reason": "New stock"
        },
        headers=auth_headers()
    )

    client.post(
        f"/api/products/{product.id}/stock-out",
        json={
            "quantity": 5,
            "reason": "Customer order"
        },
        headers=auth_headers()
    )

    response = client.get(
        f"/api/products/{product.id}/stock-history",
        headers=auth_headers()
    )

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["success"] is True
    assert response_data["message"] == "Stock history retrieved successfully"

    movements = response_data["data"]

    assert len(movements) == 2

    movement_types = {movement["type"] for movement in movements}

    assert movement_types == {"IN", "OUT"}


def test_stock_history_empty(client, monkeypatch):

    authenticate_as(monkeypatch)

    product = create_product()

    response = client.get(
        f"/api/products/{product.id}/stock-history",
        headers=auth_headers()
    )

    assert response.status_code == 200
    assert response.get_json()["data"] == []


def test_user_cannot_view_another_users_stock_history(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, user_id=202)

    product = create_product(user_id=101)

    response = client.get(
        f"/api/products/{product.id}/stock-history",
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"


def test_stock_history_invalid_product_id(client, monkeypatch):

    authenticate_as(monkeypatch)

    response = client.get(
        "/api/products/9999/stock-history",
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"


# ============================================================
# AUTHENTICATION TESTS
# ============================================================

def test_stock_in_without_authentication(client):

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-in",
        json={"quantity": 5}
    )

    assert response.status_code == 401


def test_stock_out_without_authentication(client):

    product = create_product()

    response = client.post(
        f"/api/products/{product.id}/stock-out",
        json={"quantity": 5}
    )

    assert response.status_code == 401


def test_stock_history_without_authentication(client):

    product = create_product()

    response = client.get(
        f"/api/products/{product.id}/stock-history"
    )

    assert response.status_code == 401
