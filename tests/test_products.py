
import pytest
from types import SimpleNamespace

from extensions import db
from models.categories_model import Category
from models.products_model import Product


# ============================================================
# REUSABLE TEST HELPERS
# ============================================================

def authenticate_as(monkeypatch, user_id):

    def mock_get_current_user(token):
        return SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {"id": user_id}
        )

    monkeypatch.setattr(
        "middleware.authentication.get_current_user",
        mock_get_current_user
    )


def create_category(user_id=101, name="Electronics"):

    category = Category(
        name=name,
        description="Test category",
        user_id=user_id
    )

    db.session.add(category)
    db.session.commit()

    return category


def create_product(
    category_id,
    user_id=101,
    name="Laptop",
    sku="LAP-001",
    price=50000,
    quantity=20,
    minimum_stock=5
):

    product = Product(
        name=name,
        sku=sku,
        price=price,
        quantity=quantity,
        minimum_stock=minimum_stock,
        category_id=category_id,
        user_id=user_id
    )

    db.session.add(product)
    db.session.commit()

    return product


def auth_headers():

    return {
        "Authorization": "Bearer valid-test-token"
    }


def valid_product_data(category_id):

    return {
        "name": "Laptop",
        "sku": "LAP-001",
        "price": 50000,
        "quantity": 20,
        "minimum_stock": 5,
        "category_id": category_id
    }


# ============================================================
# 1. CREATE PRODUCT TESTS
# ============================================================

def test_create_product(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    response = client.post(
        "/api/products",
        json=valid_product_data(category.id),
        headers=auth_headers()
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["success"] is True
    assert data["message"] == "Product created successfully"

    assert data["data"]["name"] == "Laptop"
    assert data["data"]["sku"] == "LAP-001"
    assert data["data"]["price"] == 50000.0
    assert data["data"]["quantity"] == 20
    assert data["data"]["category_id"] == category.id


def test_create_product_without_name(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload.pop("name")

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Product name is required"


def test_create_product_without_sku(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload.pop("sku")

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "SKU is required"


def test_create_product_without_price(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload.pop("price")

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Price is required"


def test_create_product_with_negative_price(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload["price"] = -100

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Price must be a non-negative number"
    )


def test_create_product_with_invalid_price(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload["price"] = "invalid"

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Price must be a valid number"
    )


def test_create_product_with_more_than_two_decimal_places(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload["price"] = "100.123"

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Price cannot have more than 2 decimal places"
    )


def test_create_product_with_negative_quantity(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload["quantity"] = -5

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Quantity cannot be negative"
    )


def test_create_product_with_invalid_quantity(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    payload = valid_product_data(category.id)
    payload["quantity"] = "ten"

    response = client.post(
        "/api/products",
        json=payload,
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == (
        "Quantity must be an integer"
    )


def test_create_product_with_another_users_category(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 202)

    category = create_category(user_id=101)

    response = client.post(
        "/api/products",
        json=valid_product_data(category.id),
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Category not found"


# ============================================================
# 2. GET ALL PRODUCTS TESTS
# ============================================================

def test_get_all_products(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Laptop",
        sku="LAP-001"
    )

    create_product(
        category.id,
        name="Mobile",
        sku="MOB-001"
    )

    response = client.get(
        "/api/products",
        headers=auth_headers()
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert len(data["data"]) == 2


def test_get_products_only_for_authenticated_user(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    category1 = create_category(user_id=101)

    category2 = create_category(
        user_id=202,
        name="Clothing"
    )

    create_product(
        category1.id,
        user_id=101,
        name="Laptop",
        sku="LAP-101"
    )

    create_product(
        category2.id,
        user_id=202,
        name="Shirt",
        sku="SHI-202"
    )

    response = client.get(
        "/api/products",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]

    assert len(products) == 1
    assert products[0]["name"] == "Laptop"


# ============================================================
# 3. GET PRODUCT BY ID TESTS
# ============================================================

def test_get_product_by_id(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    product = create_product(category.id)

    response = client.get(
        f"/api/products/{product.id}",
        headers=auth_headers()
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["name"] == "Laptop"


def test_get_nonexistent_product(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    response = client.get(
        "/api/products/99999",
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"


def test_user_cannot_access_another_users_product(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 202)

    category = create_category(user_id=101)

    product = create_product(
        category.id,
        user_id=101
    )

    response = client.get(
        f"/api/products/{product.id}",
        headers=auth_headers()
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "Product not found"


# ============================================================
# 4. UPDATE PRODUCT TESTS
# ============================================================

def test_update_product(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    product = create_product(category.id)

    response = client.put(
        f"/api/products/{product.id}",
        json={
            "name": "Gaming Laptop",
            "price": 75000,
            "minimum_stock": 10
        },
        headers=auth_headers()
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["success"] is True
    assert data["data"]["name"] == "Gaming Laptop"
    assert data["data"]["price"] == 75000.0
    assert data["data"]["minimum_stock"] == 10


def test_user_cannot_update_another_users_product(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 202)

    category = create_category(user_id=101)

    product = create_product(category.id, user_id=101)

    response = client.put(
        f"/api/products/{product.id}",
        json={
            "name": "Changed Product"
        },
        headers=auth_headers()
    )

    assert response.status_code == 404

    saved_product = db.session.get(Product, product.id)

    assert saved_product.name == "Laptop"


def test_quantity_cannot_be_updated_directly(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    product = create_product(category.id)

    response = client.put(
        f"/api/products/{product.id}",
        json={
            "quantity": 100
        },
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Quantity cannot be updated directly. "
        "Use the stock-in or stock-out endpoint"
    )


def test_update_product_with_invalid_price(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    product = create_product(category.id)

    response = client.put(
        f"/api/products/{product.id}",
        json={
            "price": -500
        },
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Price must be a non-negative number"
    )


def test_update_product_with_another_users_category(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    category1 = create_category(user_id=101)

    category2 = create_category(
        user_id=202,
        name="Clothing"
    )

    product = create_product(category1.id)

    response = client.put(
        f"/api/products/{product.id}",
        json={
            "category_id": category2.id
        },
        headers=auth_headers()
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Category not found"


# ============================================================
# 5. DELETE PRODUCT TESTS
# ============================================================

def test_delete_product(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    product = create_product(category.id)

    product_id = product.id

    response = client.delete(
        f"/api/products/{product_id}",
        headers=auth_headers()
    )

    assert response.status_code == 200

    assert response.get_json()["success"] is True

    deleted_product = db.session.get(Product, product_id)

    assert deleted_product is None


def test_user_cannot_delete_another_users_product(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 202)

    category = create_category(user_id=101)

    product = create_product(category.id, user_id=101)

    response = client.delete(
        f"/api/products/{product.id}",
        headers=auth_headers()
    )

    assert response.status_code == 404

    saved_product = db.session.get(Product, product.id)

    assert saved_product is not None


# ============================================================
# 6. LOW STOCK PRODUCTS
# ============================================================

def test_get_low_stock_products(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Low Stock Product",
        sku="LOW-001",
        quantity=2,
        minimum_stock=5
    )

    create_product(
        category.id,
        name="Available Product",
        sku="AVL-001",
        quantity=20,
        minimum_stock=5
    )

    response = client.get(
        "/api/products/low-stock",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]

    assert len(products) == 1
    assert products[0]["name"] == "Low Stock Product"


# ============================================================
# 7. SEARCH PRODUCTS
# ============================================================

def test_search_products(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Gaming Laptop",
        sku="GAM-001"
    )

    create_product(
        category.id,
        name="Mobile Phone",
        sku="MOB-001"
    )

    response = client.get(
        "/api/products/search?search=Laptop",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]

    assert len(products) == 1
    assert products[0]["name"] == "Gaming Laptop"


def test_search_products_with_empty_search(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    response = client.get(
        "/api/products/search?search=",
        headers=auth_headers()
    )

    assert response.status_code == 200
    assert response.get_json()["data"] == []


# ============================================================
# 8. FILTER PRODUCTS BY CATEGORY
# ============================================================

def test_filter_products_by_category(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category1 = create_category(name="Electronics")

    category2 = create_category(name="Furniture")

    create_product(
        category1.id,
        name="Laptop",
        sku="LAP-001"
    )

    create_product(
        category2.id,
        name="Chair",
        sku="CHA-001"
    )

    response = client.get(
        f"/api/products/filter/category?category_id={category1.id}",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]

    assert len(products) == 1
    assert products[0]["name"] == "Laptop"


def test_filter_products_without_category_id(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    response = client.get(
        "/api/products/filter/category",
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Valid category_id is required"
    )


# ============================================================
# 9. FILTER PRODUCTS BY PRICE
# ============================================================

def test_filter_products_by_price(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Mouse",
        sku="MOU-001",
        price=500
    )

    create_product(
        category.id,
        name="Keyboard",
        sku="KEY-001",
        price=1500
    )

    create_product(
        category.id,
        name="Monitor",
        sku="MON-001",
        price=10000
    )

    response = client.get(
        "/api/products/filter/price?min_price=1000&max_price=5000",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]

    assert len(products) == 1
    assert products[0]["name"] == "Keyboard"


def test_filter_products_with_invalid_price_range(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    response = client.get(
        "/api/products/filter/price?min_price=5000&max_price=1000",
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Minimum price cannot be greater than maximum price"
    )


# ============================================================
# 10. FILTER PRODUCTS BY STOCK
# ============================================================

@pytest.mark.parametrize(
    "stock_status,quantity,expected_count",
    [
        ("in_stock", 20, 1),
        ("low_stock", 2, 1),
        ("out_of_stock", 0, 1)
    ]
)
def test_filter_products_by_stock(
    client,
    monkeypatch,
    stock_status,
    quantity,
    expected_count
):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Test Product",
        sku="STK-001",
        quantity=quantity,
        minimum_stock=5
    )

    response = client.get(
        f"/api/products/filter/stock?stock_status={stock_status}",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]

    assert len(products) == expected_count


def test_filter_products_with_invalid_stock_status(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 101)

    response = client.get(
        "/api/products/filter/stock?stock_status=invalid",
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == "Invalid stock status"


# ============================================================
# 11. BROWSE PRODUCTS
# ============================================================

def test_browse_products_with_pagination(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    for number in range(1, 6):

        create_product(
            category.id,
            name=f"Product {number}",
            sku=f"PROD-{number:03d}"
        )

    response = client.get(
        "/api/products/browse?page=1&limit=2",
        headers=auth_headers()
    )

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert len(data["products"]) == 2

    pagination = data["pagination"]

    assert pagination["page"] == 1
    assert pagination["limit"] == 2
    assert pagination["total_items"] == 5
    assert pagination["total_pages"] == 3
    assert pagination["has_next"] is True
    assert pagination["has_prev"] is False


def test_browse_products_with_search(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Gaming Laptop",
        sku="GAM-001"
    )

    create_product(
        category.id,
        name="Mobile Phone",
        sku="MOB-001"
    )

    response = client.get(
        "/api/products/browse?search=Laptop",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]["products"]

    assert len(products) == 1
    assert products[0]["name"] == "Gaming Laptop"


def test_browse_products_with_sorting(client, monkeypatch):

    authenticate_as(monkeypatch, 101)

    category = create_category()

    create_product(
        category.id,
        name="Zebra",
        sku="ZEB-001"
    )

    create_product(
        category.id,
        name="Apple",
        sku="APP-001"
    )

    response = client.get(
        "/api/products/browse?sort=name&order=asc",
        headers=auth_headers()
    )

    assert response.status_code == 200

    products = response.get_json()["data"]["products"]

    assert products[0]["name"] == "Apple"
    assert products[1]["name"] == "Zebra"


# ============================================================
# 12. BROWSE VALIDATION TESTS
# ============================================================

@pytest.mark.parametrize(
    "query_string,expected_message",
    [
        (
            {"page": 0},
            "Page must be greater than zero"
        ),
        (
            {"limit": 0},
            "Limit must be greater than zero"
        ),
        (
            {"limit": 101},
            "Limit cannot exceed 100"
        ),
        (
            {"sort": "invalid"},
            "Invalid sort field"
        ),
        (
            {"order": "invalid"},
            "Order must be either asc or desc"
        ),
        (
            {"min_price": 5000, "max_price": 1000},
            "Minimum price cannot be greater than maximum price"
        ),
        (
            {"stock_status": "invalid"},
            "Invalid stock status"
        )
    ]
)
def test_browse_products_validation(
    client,
    monkeypatch,
    query_string,
    expected_message
):

    authenticate_as(monkeypatch, 101)

    response = client.get(
        "/api/products/browse",
        query_string=query_string,
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == expected_message


# ============================================================
# 13. BROWSE CATEGORY OWNERSHIP
# ============================================================

def test_browse_products_with_another_users_category(
    client,
    monkeypatch
):

    authenticate_as(monkeypatch, 202)

    category = create_category(user_id=101)

    response = client.get(
        f"/api/products/browse?category_id={category.id}",
        headers=auth_headers()
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == "Category not found"
