from models.stock_movements_model import StockMovement

from repositories.products_repositorie import ProductRepository
from repositories.stock_movements_repositorie import (
    StockMovementRepository
)


class StockMovementService:

    @staticmethod
    def stock_in(product_id, data, user_id):

        # Find product belonging to this user
        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        quantity = data["quantity"]

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        # Increase stock
        product.quantity += quantity

        movement = StockMovement(
            product_id=product.id,
            user_id=user_id,
            movement_type="IN",
            quantity=quantity,
            reason=data.get("reason")
        )

        ProductRepository.update()

        return StockMovementRepository.create(movement)

    @staticmethod
    def stock_out(product_id, data, user_id):

        # Find product belonging to this user
        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        quantity = data["quantity"]

        if quantity <= 0:
            raise ValueError(
                "Quantity must be greater than zero"
            )

        # Check available stock
        if quantity > product.quantity:
            raise ValueError(
                "Insufficient stock"
            )

        # Decrease stock
        product.quantity -= quantity

        movement = StockMovement(
            product_id=product.id,
            user_id=user_id,
            movement_type="OUT",
            quantity=quantity,
            reason=data.get("reason")
        )

        ProductRepository.update()

        return StockMovementRepository.create(movement)

    @staticmethod
    def get_stock_history(product_id, user_id):

        # Verify product ownership
        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        return StockMovementRepository.get_by_product(
            product_id,
            user_id
        )