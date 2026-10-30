from flask import Blueprint, request, jsonify

from services.categories_service import CategoryService
from services.categories_service import (
    CategoryService,
    UserServiceUnavailable
)

category_controller = Blueprint(
    "category_controller",
    __name__,
    url_prefix="/api/categories"
)


@category_controller.route("", methods=["POST"])
def create_category():

    data = request.get_json()

    try:

        category = CategoryService.create_category(data)

        return jsonify({
            "message": "Category created successfully",
            "id": category.id
        }), 201

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 400


@category_controller.route("", methods=["GET"])
def get_categories():

    categories = CategoryService.get_all_categories()

    return jsonify([
        {
            "id": category.id,
            "name": category.name,
            "description": category.description
        }
        for category in categories
    ])


@category_controller.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):

    try:

        category = CategoryService.get_category(
            category_id
        )

        return jsonify({
            "id": category.id,
            "name": category.name,
            "description": category.description
        })

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404


@category_controller.route(
    "/<int:category_id>",
    methods=["PUT"]
)
def update_category(category_id):

    data = request.get_json()

    try:

        category = CategoryService.update_category(
            category_id,
            data
        )

        return jsonify({
            "message": "Category updated successfully",
            "id": category.id
        })

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404


@category_controller.route(
    "/<int:category_id>",
    methods=["DELETE"]
)
def delete_category(category_id):

    try:

        CategoryService.delete_category(category_id)

        return jsonify({
            "message": "Category deleted successfully"
        })

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404





@category_controller.route("/user", methods=["GET"])
def test_user_service():

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({
            "message": "Valid Bearer token is required"
        }), 401

    token = auth_header.split(" ", 1)[1].strip()

    try:
        response = CategoryService.get_user_from_user_service(token)

    except UserServiceUnavailable as exc:
        return jsonify({
            "message": str(exc)
        }), 503

    if not response.ok:
        return jsonify({
            "message": "User service returned an error",
            "status_code": response.status_code,
            "response": response.text
        }), response.status_code

    try:
        data = response.json()

    except ValueError:
        return jsonify({
            "message": "User service returned invalid JSON"
        }), 502

    return jsonify(data), 200