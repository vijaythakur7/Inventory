
from flask import Blueprint, request, jsonify, g

from services.stock_movements_service import StockMovementService
from middleware.authentication import require_authentication


stock_controller = Blueprint(
    "stock_controller",
    __name__,
    url_prefix="/api/products"
)


# ============================================================
# STOCK IN
# ============================================================

@stock_controller.route(
    "/<int:product_id>/stock-in",
    methods=["POST"]
)
@require_authentication
def stock_in(product_id):

    user_id = g.user_id

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
        status_code = 404 if str(error) == "Product not found" else 400

        return jsonify({
            "error": str(error)
        }), status_code


# ============================================================
# STOCK OUT
# ============================================================

@stock_controller.route(
    "/<int:product_id>/stock-out",
    methods=["POST"]
)
@require_authentication
def stock_out(product_id):

    user_id = g.user_id

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
        status_code = 404 if str(error) == "Product not found" else 400

        return jsonify({
            "error": str(error)
        }), status_code


# ============================================================
# STOCK HISTORY
# ============================================================

@stock_controller.route(
    "/<int:product_id>/stock-history",
    methods=["GET"]
)
@require_authentication
def stock_history(product_id):

    user_id = g.user_id

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
