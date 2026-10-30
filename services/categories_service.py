from models.categories_model import Category
from repositories.categories_repositorie import CategoryRepository
from clients.user_client import (
    get_current_user,
    UserServiceUnavailable as UserClientUnavailable
)


class CategoryService:

    @staticmethod
    def create_category(data):

        category = Category(
            name=data["name"],
            description=data.get("description")
        )

        return CategoryRepository.create(category)

    @staticmethod
    def get_all_categories():

        return CategoryRepository.get_all()

    @staticmethod
    def get_category(category_id):

        category = CategoryRepository.get_by_id(category_id)

        if not category:
            raise ValueError("Category not found")

        return category

    @staticmethod
    def update_category(category_id, data):

        category = CategoryRepository.get_by_id(category_id)

        if not category:
            raise ValueError("Category not found")

        category.name = data.get("name", category.name)
        category.description = data.get(
            "description",
            category.description
        )

        CategoryRepository.update()

        return category

    @staticmethod
    def delete_category(category_id):

        category = CategoryRepository.get_by_id(category_id)

        if not category:
            raise ValueError("Category not found")

        CategoryRepository.delete(category)

    @staticmethod
    def get_user_from_user_service(token):

        try:
            response = get_current_user(token)
            return response

        except UserClientUnavailable as exc:
            raise UserServiceUnavailable(str(exc)) from exc

class UserServiceUnavailable(Exception):
    pass