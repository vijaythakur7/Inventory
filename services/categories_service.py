from models.categories_model import Category
from repositories.categories_repositorie import CategoryRepository


class CategoryService:

    @staticmethod
    def create_category(data, user_id):

        category = Category(
            name=data["name"],
            description=data.get("description"),
            user_id=user_id
        )

        return CategoryRepository.create(category)

    @staticmethod
    def get_all_categories(user_id):

        return CategoryRepository.get_all(user_id)

    @staticmethod
    def get_category(category_id, user_id):

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        return category

    @staticmethod
    def update_category(category_id, data, user_id):

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

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
    def delete_category(category_id, user_id):

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        CategoryRepository.delete(category)
