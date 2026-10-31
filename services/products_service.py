from models.products_model import Product
from repositories.products_repositorie import ProductRepository
from repositories.categories_repositorie import CategoryRepository


class ProductService:

    @staticmethod
    def create_product(data, user_id):

        # Check whether category belongs to this user
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

        product.name = data.get(
            "name",
            product.name
        )

        product.sku = data.get(
            "sku",
            product.sku
        )

        product.price = data.get(
            "price",
            product.price
        )

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

        # Verify category ownership first
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