
from flask import Blueprint, request, jsonify, g

from services.categories_service import CategoryService
from middleware.authentication import require_authentication


category_controller = Blueprint(
    "category_controller",
    __name__,
    url_prefix="/api/categories"
)


# ============================================================
# CREATE CATEGORY
# ============================================================

@category_controller.route("", methods=["POST"])
@require_authentication
def create_category():

    user_id = g.user_id

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


# ============================================================
# GET ALL CATEGORIES
# ============================================================

@category_controller.route("", methods=["GET"])
@require_authentication
def get_categories():

    user_id = g.user_id

    categories = CategoryService.get_all_categories(user_id)

    return jsonify([
        {
            "id": category.id,
            "name": category.name,
            "description": category.description
        }
        for category in categories
    ]), 200


# ============================================================
# GET CATEGORY BY ID
# ============================================================

@category_controller.route("/<int:category_id>", methods=["GET"])
@require_authentication
def get_category(category_id):

    user_id = g.user_id

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


# ============================================================
# UPDATE CATEGORY
# ============================================================

@category_controller.route(
    "/<int:category_id>",
    methods=["PUT"]
)
@require_authentication
def update_category(category_id):

    user_id = g.user_id

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
        status_code = 404 if str(error) == "Category not found" else 400

        return jsonify({
            "error": str(error)
        }), status_code


# ============================================================
# DELETE CATEGORY
# ============================================================

@category_controller.route(
    "/<int:category_id>",
    methods=["DELETE"]
)
@require_authentication
def delete_category(category_id):

    user_id = g.user_id

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


# ============================================================
# TEST USER SERVICE COMMUNICATION
# ============================================================

@category_controller.route("/user", methods=["GET"])
@require_authentication
def test_user_service():

    user_id = g.user_id

    return jsonify({
        "message": "User Service communication successful",
        "user_id": user_id
    }), 200
