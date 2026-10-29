from extensions import db
from models.products_model import Product


class ProductRepository:

    @staticmethod
    def create(product):
        db.session.add(product)
        db.session.commit()

        return product

    @staticmethod
    def get_all():
        return Product.query.all()

    @staticmethod
    def get_by_id(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(product):
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def get_by_category(category_id):
        return Product.query.filter_by(
            category_id=category_id
        ).all()

    @staticmethod
    def get_low_stock():
        return Product.query.filter(
            Product.quantity <= Product.minimum_stock
        ).all()