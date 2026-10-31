from flask import Blueprint, request, jsonify

from services.categories_service import (
    CategoryService,
    UserServiceUnavailable
)

category_controller = Blueprint(
    "category_controller",
    __name__,
    url_prefix="/api/categories"
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
                "message": "User service returned invalid JSON"
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


@category_controller.route("", methods=["POST"])
def create_category():

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    data = request.get_json()

    if not isinstance(data, dict) or not data.get("name"):
        return jsonify({
            "error": "Category name is required"
        }), 400

    try:
        category = CategoryService.create_category(
            data,
            user_id
        )

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

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    categories = CategoryService.get_all_categories(user_id)

    return jsonify([
        {
            "id": category.id,
            "name": category.name,
            "description": category.description
        }
        for category in categories
    ]), 200


@category_controller.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    try:
        category = CategoryService.get_category(
            category_id,
            user_id
        )

        return jsonify({
            "id": category.id,
            "name": category.name,
            "description": category.description
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404


@category_controller.route(
    "/<int:category_id>",
    methods=["PUT"]
)
def update_category(category_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid JSON body is required"
        }), 400

    try:
        category = CategoryService.update_category(
            category_id,
            data,
            user_id
        )

        return jsonify({
            "message": "Category updated successfully",
            "id": category.id
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404


@category_controller.route(
    "/<int:category_id>",
    methods=["DELETE"]
)
def delete_category(category_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    try:
        CategoryService.delete_category(
            category_id,
            user_id
        )

        return jsonify({
            "message": "Category deleted successfully"
        }), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404


@category_controller.route("/user", methods=["GET"])
def test_user_service():

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    return jsonify({
        "message": "User Service communication successful",
        "user_id": user_id
    }), 200