from extensions import db
from models.stock_movements_model import StockMovement


class StockMovementRepository:

    @staticmethod
    def create(movement):
        db.session.add(movement)
        db.session.commit()

        return movement

    @staticmethod
    def get_by_product(product_id):
        return StockMovement.query.filter_by(
            product_id=product_id
        ).all()