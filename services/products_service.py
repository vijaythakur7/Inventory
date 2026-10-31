from decimal import Decimal, InvalidOperation
from models.products_model import Product
from repositories.products_repositorie import ProductRepository
from repositories.categories_repositorie import CategoryRepository


class ProductService:

    @staticmethod
    def create_product(data, user_id):

        category = CategoryRepository.get_by_id(
            data["category_id"],
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        product = Product(
            name=data["name"],
            sku=data["sku"],
            price=data["price"],
            quantity=data.get("quantity", 0),
            minimum_stock=data.get("minimum_stock", 5),
            category_id=data["category_id"],
            user_id=user_id
        )

        return ProductRepository.create(product)

    @staticmethod
    def get_all_products(user_id):
        return ProductRepository.get_all(user_id)

    @staticmethod
    def get_product(product_id, user_id):

        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        return product

    @staticmethod
    def update_product(product_id, data, user_id):

        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        product.name = data.get("name", product.name)
        product.sku = data.get("sku", product.sku)
        product.price = data.get("price", product.price)
        product.minimum_stock = data.get(
            "minimum_stock",
            product.minimum_stock
        )

        if "category_id" in data:

            category = CategoryRepository.get_by_id(
                data["category_id"],
                user_id
            )

            if not category:
                raise ValueError("Category not found")

            product.category_id = data["category_id"]

        ProductRepository.update()

        return product

    @staticmethod
    def delete_product(product_id, user_id):

        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        ProductRepository.delete(product)

    @staticmethod
    def get_products_by_category(category_id, user_id):

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        return ProductRepository.get_by_category(
            category_id,
            user_id
        )

    @staticmethod
    def get_low_stock_products(user_id):
        return ProductRepository.get_low_stock(user_id)

    # SEARCH PRODUCT
    @staticmethod
    def search_products(search, user_id):

        if not search or not search.strip():
            return []

        return ProductRepository.search_products(
            search.strip(),
            user_id
        )

    # FILTER BY CATEGORY
    @staticmethod
    def filter_by_category(category_id, user_id):

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        return ProductRepository.filter_by_category(
            category_id,
            user_id
        )

    # FILTER BY PRICE
    @staticmethod
    def filter_by_price(
        user_id,
        min_price=None,
        max_price=None
    ):

        min_price = ProductService._validate_price(min_price)
        max_price = ProductService._validate_price(max_price)

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise ValueError(
                "Minimum price cannot be greater than maximum price"
            )

        return ProductRepository.filter_by_price(
            user_id,
            min_price,
            max_price
        )

    # FILTER BY STOCK
    @staticmethod
    def filter_by_stock(stock_status, user_id):

        allowed_status = [
            "in_stock",
            "low_stock",
            "out_of_stock"
        ]

        if stock_status not in allowed_status:
            raise ValueError("Invalid stock status")

        return ProductRepository.filter_by_stock(
            stock_status,
            user_id
        )

    # SEARCH + FILTER + SORT + PAGINATION
    @staticmethod
    def get_products(
        user_id,
        search=None,
        category_id=None,
        stock_status=None,
        min_price=None,
        max_price=None,
        sort="created_at",
        order="desc",
        page=1,
        limit=10
    ):

        if page < 1:
            page = 1

        if limit < 1:
            limit = 10

        if limit > 100:
            limit = 100

        if order not in ["asc", "desc"]:
            order = "desc"

        allowed_sort = [
            "name",
            "price",
            "quantity",
            "created_at",
            "updated_at"
        ]

        if sort not in allowed_sort:
            sort = "created_at"

        min_price = ProductService._validate_price(min_price)
        max_price = ProductService._validate_price(max_price)

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise ValueError(
                "Minimum price cannot be greater than maximum price"
            )

        if stock_status is not None and stock_status not in [
            "in_stock",
            "low_stock",
            "out_of_stock"
        ]:
            raise ValueError("Invalid stock status")

        if category_id is not None:
            category = CategoryRepository.get_by_id(
                category_id,
                user_id
            )

            if not category:
                raise ValueError("Category not found")

        return ProductRepository.get_products(
            user_id=user_id,
            search=search.strip() if search else None,
            category_id=category_id,
            stock_status=stock_status,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            order=order,
            page=page,
            limit=limit
        )

    @staticmethod
    def _validate_price(value):

        if value is None:
            return None

        try:
            price = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValueError("Price must be a valid number")

        if not price.is_finite() or price < 0:
            raise ValueError("Price must be a non-negative number")

        return price
