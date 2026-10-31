
from models.categories_model import Category
from repositories.categories_repositorie import CategoryRepository


class CategoryService:

    # ============================================================
    # REUSABLE VALIDATION HELPERS
    # ============================================================

    @staticmethod
    def _validate_required_string(value, field_name, max_length):

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} is required")

        value = value.strip()

        if len(value) > max_length:
            raise ValueError(
                f"{field_name} cannot exceed {max_length} characters"
            )

        return value

    @staticmethod
    def _validate_optional_string(value, field_name, max_length):

        if value is None:
            return None

        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        value = value.strip()

        if len(value) > max_length:
            raise ValueError(
                f"{field_name} cannot exceed {max_length} characters"
            )

        return value or None

    @staticmethod
    def _validate_category_id(category_id):

        if isinstance(category_id, bool) or not isinstance(category_id, int):
            raise ValueError("Category ID must be an integer")

        if category_id <= 0:
            raise ValueError("Category ID must be greater than zero")

        return category_id

    # ============================================================
    # CREATE CATEGORY
    # ============================================================

    @staticmethod
    def create_category(data, user_id):

        if not isinstance(data, dict):
            raise ValueError("Valid category data is required")

        name = CategoryService._validate_required_string(
            data.get("name"),
            "Category name",
            100
        )

        description = CategoryService._validate_optional_string(
            data.get("description"),
            "Description",
            255
        )

        category = Category(
            name=name,
            description=description,
            user_id=user_id
        )

        return CategoryRepository.create(category)

    # ============================================================
    # GET ALL CATEGORIES
    # ============================================================

    @staticmethod
    def get_all_categories(user_id):

        return CategoryRepository.get_all(user_id)

    # ============================================================
    # GET CATEGORY BY ID
    # ============================================================

    @staticmethod
    def get_category(category_id, user_id):

        category_id = CategoryService._validate_category_id(
            category_id
        )

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        return category

    # ============================================================
    # UPDATE CATEGORY
    # ============================================================

    @staticmethod
    def update_category(category_id, data, user_id):

        category_id = CategoryService._validate_category_id(
            category_id
        )

        if not isinstance(data, dict) or not data:
            raise ValueError("Valid category data is required")

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        if "name" in data:
            category.name = CategoryService._validate_required_string(
                data["name"],
                "Category name",
                100
            )

        if "description" in data:
            category.description = (
                CategoryService._validate_optional_string(
                    data["description"],
                    "Description",
                    255
                )
            )

        CategoryRepository.update()

        return category

    # ============================================================
    # DELETE CATEGORY
    # ============================================================

    @staticmethod
    def delete_category(category_id, user_id):

        category_id = CategoryService._validate_category_id(
            category_id
        )

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        CategoryRepository.delete(category)
