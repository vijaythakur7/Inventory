
from flask import Blueprint, request, g

from services.categories_service import CategoryService
from middleware.authentication import require_authentication
from utils.response import success_response, error_response


category_controller = Blueprint(
    "category_controller",
    __name__,
    url_prefix="/api/categories"
)


# ============================================================
# CATEGORY RESPONSE FORMAT
# ============================================================

def serialize_category(category):

    return {
        "id": category.id,
        "name": category.name,
        "description": category.description
    }


# ============================================================
# CREATE CATEGORY
# ============================================================

@category_controller.route("", methods=["POST"])
@require_authentication
def create_category():

    user_id = g.user_id
    data = request.get_json()

    if not isinstance(data, dict) or not data.get("name"):
        return error_response("Category name is required", 400)

    try:
        category = CategoryService.create_category(
            data,
            user_id
        )

        return success_response(
            "Category created successfully",
            serialize_category(category),
            201
        )

    except ValueError as error:
        return error_response(str(error), 400)


# ============================================================
# GET ALL CATEGORIES
# ============================================================

@category_controller.route("", methods=["GET"])
@require_authentication
def get_categories():

    user_id = g.user_id

    categories = CategoryService.get_all_categories(user_id)

    return success_response(
        "Categories retrieved successfully",
        [
            serialize_category(category)
            for category in categories
        ]
    )


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

        return success_response(
            "Category retrieved successfully",
            serialize_category(category)
        )

    except ValueError as error:
        return error_response(str(error), 404)


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
        return error_response("Valid JSON body is required", 400)

    try:
        category = CategoryService.update_category(
            category_id,
            data,
            user_id
        )

        return success_response(
            "Category updated successfully",
            serialize_category(category)
        )

    except ValueError as error:
        status_code = 404 if str(error) == "Category not found" else 400

        return error_response(str(error), status_code)


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

        return success_response(
            "Category deleted successfully"
        )

    except ValueError as error:
        return error_response(str(error), 404)


# ============================================================
# TEST USER SERVICE COMMUNICATION
# ============================================================

@category_controller.route("/user", methods=["GET"])
@require_authentication
def test_user_service():

    user_id = g.user_id

    return success_response(
        "User Service communication successful",
        {
            "user_id": user_id
        }
    )
