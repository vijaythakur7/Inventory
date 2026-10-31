
from decimal import Decimal, InvalidOperation

from models.products_model import Product
from repositories.products_repositorie import ProductRepository
from repositories.categories_repositorie import CategoryRepository


class ProductService:

    # ============================================================
    # REUSABLE VALIDATION HELPERS
    # ============================================================

    @staticmethod
    def _validate_required_string(value, field_name):

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} is required")

        return value.strip()

    @staticmethod
    def _validate_non_negative_integer(value, field_name):

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer")

        if value < 0:
            raise ValueError(f"{field_name} cannot be negative")

        return value

    @staticmethod
    def _validate_positive_integer(value, field_name):

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer")

        if value < 1:
            raise ValueError(f"{field_name} must be greater than zero")

        return value

    @staticmethod
    def _validate_price(value):

        if value is None:
            return None

        try:
            price = Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Price must be a valid number")

        if not price.is_finite() or price < 0:
            raise ValueError("Price must be a non-negative number")

        if price.as_tuple().exponent < -2:
            raise ValueError("Price cannot have more than 2 decimal places")

        if price >= Decimal("100000000"):
            raise ValueError("Price exceeds the maximum allowed value")

        return price

    # ============================================================
    # CREATE PRODUCT
    # ============================================================

    @staticmethod
    def create_product(data, user_id):

        if not isinstance(data, dict):
            raise ValueError("Valid product data is required")

        name = ProductService._validate_required_string(
            data.get("name"),
            "Product name"
        )

        sku = ProductService._validate_required_string(
            data.get("sku"),
            "SKU"
        )

        price = ProductService._validate_price(data.get("price"))

        if price is None:
            raise ValueError("Price is required")

        quantity = ProductService._validate_non_negative_integer(
            data.get("quantity", 0),
            "Quantity"
        )

        minimum_stock = ProductService._validate_non_negative_integer(
            data.get("minimum_stock", 5),
            "Minimum stock"
        )

        category_id = ProductService._validate_positive_integer(
            data.get("category_id"),
            "Category ID"
        )

        category = CategoryRepository.get_by_id(
            category_id,
            user_id
        )

        if not category:
            raise ValueError("Category not found")

        product = Product(
            name=name,
            sku=sku,
            price=price,
            quantity=quantity,
            minimum_stock=minimum_stock,
            category_id=category_id,
            user_id=user_id
        )

        return ProductRepository.create(product)

    # ============================================================
    # GET ALL PRODUCTS
    # ============================================================

    @staticmethod
    def get_all_products(user_id):

        return ProductRepository.get_all(user_id)

    # ============================================================
    # GET PRODUCT BY ID
    # ============================================================

    @staticmethod
    def get_product(product_id, user_id):

        product_id = ProductService._validate_positive_integer(
            product_id,
            "Product ID"
        )

        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        return product

    # ============================================================
    # UPDATE PRODUCT
    # ============================================================

    @staticmethod
    def update_product(product_id, data, user_id):

        product_id = ProductService._validate_positive_integer(
            product_id,
            "Product ID"
        )

        if not isinstance(data, dict) or not data:
            raise ValueError("Valid product data is required")

        product = ProductRepository.get_by_id(
            product_id,
            user_id
        )

        if not product:
            raise ValueError("Product not found")

        if "name" in data:
            product.name = ProductService._validate_required_string(
                data["name"],
                "Product name"
            )

        if "sku" in data:
            product.sku = ProductService._validate_required_string(
                data["sku"],
                "SKU"
            )

        if "price" in data:
            price = ProductService._validate_price(data["price"])

            if price is None:
                raise ValueError("Price is required")

            product.price = price

        if "minimum_stock" in data:
            product.minimum_stock = (
                ProductService._validate_non_negative_integer(
                    data["minimum_stock"],
                    "Minimum stock"
                )
            )

        if "quantity" in data:
            raise ValueError(
                "Quantity cannot be updated directly. "
                "Use the stock-in or stock-out endpoint"
            )

        if "category_id" in data:

            category_id = ProductService._validate_positive_integer(
                data["category_id"],
                "Category ID"
            )

            category = CategoryRepository.get_by_id(
                category_id,
                user_id
            )

            if not category:
                raise ValueError("Category not found")

            product.category_id = category_id

        ProductRepository.update()

        return product

    # ============================================================
    # DELETE PRODUCT
    # ============================================================

    @staticmethod
    def delete_product(product_id, user_id):

        product = ProductService.get_product(product_id, user_id)

        ProductRepository.delete(product)

    # ============================================================
    # GET PRODUCTS BY CATEGORY
    # ============================================================

    @staticmethod
    def get_products_by_category(category_id, user_id):

        category_id = ProductService._validate_positive_integer(
            category_id,
            "Category ID"
        )

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

    # ============================================================
    # LOW STOCK PRODUCTS
    # ============================================================

    @staticmethod
    def get_low_stock_products(user_id):

        return ProductRepository.get_low_stock(user_id)

    # ============================================================
    # SEARCH PRODUCTS
    # ============================================================

    @staticmethod
    def search_products(search, user_id):

        if search is None or not isinstance(search, str):
            return []

        search = search.strip()

        if not search:
            return []

        return ProductRepository.search_products(
            search,
            user_id
        )

    # ============================================================
    # FILTER BY CATEGORY
    # ============================================================

    @staticmethod
    def filter_by_category(category_id, user_id):

        category_id = ProductService._validate_positive_integer(
            category_id,
            "Category ID"
        )

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

    # ============================================================
    # FILTER BY PRICE
    # ============================================================

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

    # ============================================================
    # FILTER BY STOCK
    # ============================================================

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

    # ============================================================
    # SEARCH + FILTER + SORT + PAGINATION
    # ============================================================

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

        # Validate page

        page = ProductService._validate_positive_integer(
            page,
            "Page"
        )

        # Validate limit

        limit = ProductService._validate_positive_integer(
            limit,
            "Limit"
        )

        if limit > 100:
            raise ValueError("Limit cannot exceed 100")

        # Validate sorting

        if not isinstance(order, str) or order not in ["asc", "desc"]:
            raise ValueError("Order must be either asc or desc")

        allowed_sort = [
            "name",
            "price",
            "quantity",
            "created_at",
            "updated_at"
        ]

        if not isinstance(sort, str) or sort not in allowed_sort:
            raise ValueError("Invalid sort field")

        # Validate search

        if search is not None:
            if not isinstance(search, str):
                raise ValueError("Search must be a string")

            search = search.strip() or None

        # Validate prices

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

        # Validate stock status

        allowed_status = [
            "in_stock",
            "low_stock",
            "out_of_stock"
        ]

        if stock_status is not None:
            if stock_status not in allowed_status:
                raise ValueError("Invalid stock status")

        # Validate category ownership

        if category_id is not None:

            category_id = ProductService._validate_positive_integer(
                category_id,
                "Category ID"
            )

            category = CategoryRepository.get_by_id(
                category_id,
                user_id
            )

            if not category:
                raise ValueError("Category not found")

        return ProductRepository.get_products(
            user_id=user_id,
            search=search,
            category_id=category_id,
            stock_status=stock_status,
            min_price=min_price,
            max_price=max_price,
            sort=sort,
            order=order,
            page=page,
            limit=limit
        )
