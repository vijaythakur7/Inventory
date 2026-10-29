from flask import Blueprint, request, jsonify

from services.stock_movements_service import (
    StockMovementService
)


stock_controller = Blueprint(
    "stock_controller",
    __name__,
    url_prefix="/api/products"
)


@stock_controller.route(
    "/<int:product_id>/stock-in",
    methods=["POST"]
)
def stock_in(product_id):

    data = request.get_json()

    try:

        movement = StockMovementService.stock_in(
            product_id,
            data
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

    data = request.get_json()

    try:

        movement = StockMovementService.stock_out(
            product_id,
            data
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

    try:

        movements = (
            StockMovementService
            .get_stock_history(product_id)
        )

        return jsonify([
            {
                "id": movement.id,
                "type": movement.movement_type,
                "quantity": movement.quantity,
                "reason": movement.reason,
                "created_at": movement.created_at
            }
            for movement in movements
        ])

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404