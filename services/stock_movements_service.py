
from models.stock_movements_model import StockMovement

from extensions import db

from repositories.products_repositorie import ProductRepository
from repositories.stock_movements_repositorie import (
    StockMovementRepository
)


class StockMovementService:

    # ============================================================
    # VALIDATION HELPERS
    # ============================================================

    @staticmethod
    def _validate_quantity(value):

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Quantity must be an integer")

        if value <= 0:
            raise ValueError("Quantity must be greater than zero")

        return value

    @staticmethod
    def _validate_reason(value):

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError("Reason must be a string")

        value = value.strip()

        if len(value) > 255:
            raise ValueError("Reason cannot exceed 255 characters")

        return value or None

    @staticmethod
    def _validate_request_data(data):

        if not isinstance(data, dict):
            raise ValueError("Valid request data is required")

        if "quantity" not in data:
            raise ValueError("Quantity is required")

        quantity = StockMovementService._validate_quantity(
            data["quantity"]
        )

        reason = StockMovementService._validate_reason(
            data.get("reason")
        )

        return quantity, reason

    # ============================================================
    # STOCK IN
    # ============================================================

    @staticmethod
    def stock_in(product_id, data, user_id):

        quantity, reason = (
            StockMovementService._validate_request_data(data)
        )

        product = ProductRepository.get_by_id_for_update(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        try:
            product.quantity += quantity

            movement = StockMovement(
                product_id=product.id,
                user_id=user_id,
                movement_type="IN",
                quantity=quantity,
                reason=reason
            )

            db.session.add(movement)
            db.session.commit()

            return movement

        except Exception:
            db.session.rollback()
            raise

    # ============================================================
    # STOCK OUT
    # ============================================================

    @staticmethod
    def stock_out(product_id, data, user_id):

        quantity, reason = (
            StockMovementService._validate_request_data(data)
        )

        product = ProductRepository.get_by_id_for_update(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        if quantity > product.quantity:
            raise ValueError("Insufficient stock")

        try:
            product.quantity -= quantity

            movement = StockMovement(
                product_id=product.id,
                user_id=user_id,
                movement_type="OUT",
                quantity=quantity,
                reason=reason
            )

            db.session.add(movement)
            db.session.commit()

            return movement

        except Exception:
            db.session.rollback()
            raise

    # ============================================================
    # STOCK HISTORY
    # ============================================================

    @staticmethod
    def get_stock_history(product_id, user_id):

        if (
            isinstance(product_id, bool)
            or not isinstance(product_id, int)
            or product_id <= 0
        ):
            raise ValueError("Product ID must be a positive integer")

        product = ProductRepository.get_by_id_for_update(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        return StockMovementRepository.get_by_product(
            product_id,
            user_id
        )
