from extensions import db
from models.products_model import Product


class ProductRepository:

    @staticmethod
    def create(product):
        db.session.add(product)
        db.session.commit()

        return product

    @staticmethod
    def get_all(user_id):
        return Product.query.filter_by(
            user_id=user_id
        ).all()

    @staticmethod
    def get_by_id(product_id, user_id):
        return Product.query.filter_by(
            id=product_id,
            user_id=user_id
        ).first()

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(product):
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def get_by_category(category_id, user_id):
        return Product.query.filter_by(
            category_id=category_id,
            user_id=user_id
        ).all()

    @staticmethod
    def get_low_stock(user_id):
        return Product.query.filter(
            Product.user_id == user_id,
            Product.quantity <= Product.minimum_stock
        ).all()