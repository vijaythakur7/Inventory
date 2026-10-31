from extensions import db
from models.categories_model import Category

class CategoryRepository:

    @staticmethod
    def create(category):
        db.session.add(category)
        db.session.commit()

        return category

    @staticmethod
    def get_all(user_id):
        return Category.query.filter_by(
            user_id=user_id
        ).all()

    @staticmethod
    def get_by_id(category_id,user_id):
        return Category.query.filter_by(
            id=category_id,
            user_id=user_id
        ).first()

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(category):
        db.session.delete(category)
        db.session.commit()