from extensions import db
from models.categories_model import Category

class CategoryRepository:

    @staticmethod
    def create(category):
        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def get_all():
        return Category.query.all()

    @staticmethod
    def get_by_id(category_id):
        return Category.query.get(category_id)

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(category):
        db.session.delete(category)
        db.session.commit()