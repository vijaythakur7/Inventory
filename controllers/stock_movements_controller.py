
from flask import Blueprint, request, g

from services.stock_movements_service import StockMovementService
from middleware.authentication import require_authentication
from utils.response import success_response, error_response


stock_controller = Blueprint(
    "stock_controller",
    __name__,
    url_prefix="/api/products"
)


# ============================================================
# STOCK MOVEMENT RESPONSE FORMAT
# ============================================================

def serialize_stock_movement(movement):

    return {
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
        return error_response("Quantity is required", 400)

    try:
        movement = StockMovementService.stock_in(
            product_id,
            data,
            user_id
        )

        return success_response(
            "Stock added successfully",
            {
                "movement_id": movement.id,
                "movement": serialize_stock_movement(movement)
            },
            201
        )

    except ValueError as error:
        status_code = 404 if str(error) == "Product not found" else 400

        return error_response(str(error), status_code)


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
        return error_response("Quantity is required", 400)

    try:
        movement = StockMovementService.stock_out(
            product_id,
            data,
            user_id
        )

        return success_response(
            "Stock removed successfully",
            {
                "movement_id": movement.id,
                "movement": serialize_stock_movement(movement)
            },
            201
        )

    except ValueError as error:
        status_code = 404 if str(error) == "Product not found" else 400

        return error_response(str(error), status_code)


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

        return success_response(
            "Stock history retrieved successfully",
            [
                serialize_stock_movement(movement)
                for movement in movements
            ]
        )

    except ValueError as error:
        return error_response(str(error), 404)
