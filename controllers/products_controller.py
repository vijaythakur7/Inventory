from flask import Blueprint, request, jsonify

from services.products_service import ProductService
from services.categories_service import (
    CategoryService,
    UserServiceUnavailable
)


product_controller = Blueprint(
    "product_controller",
    __name__,
    url_prefix="/api/products"
)


def get_authenticated_user():

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
        response = CategoryService.get_user_from_user_service(token)

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
                "message": "Authentication failed",
                "status_code": response.status_code
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


@product_controller.route("", methods=["POST"])
def create_product():

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON body is required"
        }), 400

    try:
        product = ProductService.create_product(
            data,
            user_id
        )

        return jsonify({
            "message": "Product created successfully",
            "id": product.id
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


@product_controller.route("", methods=["GET"])
def get_products():

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    products = ProductService.get_all_products(user_id)

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "quantity": product.quantity,
            "minimum_stock": product.minimum_stock,
            "category_id": product.category_id
        }
        for product in products
    ]), 200


@product_controller.route(
    "/<int:product_id>",
    methods=["GET"]
)
def get_product(product_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    try:
        product = ProductService.get_product(
            product_id,
            user_id
        )

        return jsonify({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "quantity": product.quantity,
            "minimum_stock": product.minimum_stock,
            "category_id": product.category_id
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404


@product_controller.route(
    "/<int:product_id>",
    methods=["PUT"]
)
def update_product(product_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON body is required"
        }), 400

    try:
        product = ProductService.update_product(
            product_id,
            data,
            user_id
        )

        return jsonify({
            "message": "Product updated successfully",
            "id": product.id
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404


@product_controller.route(
    "/<int:product_id>",
    methods=["DELETE"]
)
def delete_product(product_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    try:
        ProductService.delete_product(
            product_id,
            user_id
        )

        return jsonify({
            "message": "Product deleted successfully"
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404


@product_controller.route(
    "/low-stock",
    methods=["GET"]
)
def get_low_stock_products():

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    products = ProductService.get_low_stock_products(user_id)

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "quantity": product.quantity,
            "minimum_stock": product.minimum_stock
        }
        for product in products
    ]), 200