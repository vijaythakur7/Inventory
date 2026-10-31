
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
        return Product.query.filter_by(user_id=user_id).all()

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

    # SEARCH
    @staticmethod
    def search_products(search, user_id):
        return Product.query.filter(
            Product.user_id == user_id,
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        ).all()

    # FILTER BY CATEGORY
    @staticmethod
    def filter_by_category(category_id, user_id):
        return Product.query.filter_by(
            category_id=category_id,
            user_id=user_id
        ).all()

    # FILTER BY PRICE
    @staticmethod
    def filter_by_price(user_id, min_price=None, max_price=None):
        query = Product.query.filter_by(user_id=user_id)

        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        return query.all()

    # FILTER BY STOCK
    @staticmethod
    def filter_by_stock(stock_status, user_id):
        query = Product.query.filter_by(user_id=user_id)

        if stock_status == "in_stock":
            query = query.filter(
                Product.quantity > Product.minimum_stock
            )

        elif stock_status == "low_stock":
            query = query.filter(
                Product.quantity <= Product.minimum_stock,
                Product.quantity > 0
            )

        elif stock_status == "out_of_stock":
            query = query.filter(Product.quantity == 0)

        return query.all()

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
        # Always restrict results to the authenticated owner.
        query = Product.query.filter_by(user_id=user_id)

        # SEARCH
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
            )

        # CATEGORY FILTER
        if category_id is not None:
            query = query.filter(
                Product.category_id == category_id
            )

        # STOCK FILTER
        if stock_status == "in_stock":
            query = query.filter(
                Product.quantity > Product.minimum_stock
            )

        elif stock_status == "low_stock":
            query = query.filter(
                Product.quantity <= Product.minimum_stock,
                Product.quantity > 0
            )

        elif stock_status == "out_of_stock":
            query = query.filter(Product.quantity == 0)

        # PRICE FILTER
        if min_price is not None:
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        # SORTING
        sort_columns = {
            "name": Product.name,
            "price": Product.price,
            "quantity": Product.quantity,
            "created_at": Product.created_at,
            "updated_at": Product.updated_at
        }

        sort_column = sort_columns.get(sort, Product.created_at)

        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        # PAGINATION
        return query.paginate(
            page=page,
            per_page=limit,
            error_out=False
        )
