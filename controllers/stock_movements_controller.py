from flask import Blueprint, request, jsonify

from services.stock_movements_service import (
    StockMovementService
)

from services.categories_service import (
    CategoryService,
    UserServiceUnavailable
)


stock_controller = Blueprint(
    "stock_controller",
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


@stock_controller.route(
    "/<int:product_id>/stock-in",
    methods=["POST"]
)
def stock_in(product_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    data = request.get_json()

    if not isinstance(data, dict) or "quantity" not in data:
        return jsonify({
            "error": "Quantity is required"
        }), 400

    try:
        movement = StockMovementService.stock_in(
            product_id,
            data,
            user_id
        )

        return jsonify({
            "message": "Stock added successfully",
            "movement_id": movement.id
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


@stock_controller.route(
    "/<int:product_id>/stock-out",
    methods=["POST"]
)
def stock_out(product_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    data = request.get_json()

    if not isinstance(data, dict) or "quantity" not in data:
        return jsonify({
            "error": "Quantity is required"
        }), 400

    try:
        movement = StockMovementService.stock_out(
            product_id,
            data,
            user_id
        )

        return jsonify({
            "message": "Stock removed successfully",
            "movement_id": movement.id
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400


@stock_controller.route(
    "/<int:product_id>/stock-history",
    methods=["GET"]
)
def stock_history(product_id):

    user_id, error_response = get_authenticated_user()

    if error_response:
        return error_response

    try:
        movements = StockMovementService.get_stock_history(
            product_id,
            user_id
        )

        return jsonify([
            {
                "id": movement.id,
                "type": movement.movement_type,
                "quantity": movement.quantity,
                "reason": movement.reason,
                "created_at": (
                    movement.created_at.isoformat()
                    if movement.created_at
                    else None
                )
            }
            for movement in movements
        ]), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404