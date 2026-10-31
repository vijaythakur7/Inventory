from flask import Blueprint, request, jsonify, g

from services.products_service import ProductService
from middleware.authentication import require_authentication


product_controller = Blueprint(
    "product_controller",
    __name__,
    url_prefix="/api/products"
)


# ============================================================
# PRODUCT RESPONSE FORMAT
# ============================================================

def serialize_product(product):

    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "price": float(product.price),
        "quantity": product.quantity,
        "minimum_stock": product.minimum_stock,
        "category_id": product.category_id
    }


# ============================================================
# CREATE PRODUCT
# ============================================================

@product_controller.route("", methods=["POST"])
@require_authentication
def create_product():

    user_id = g.user_id

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body is required"}), 400

    try:
        product = ProductService.create_product(data, user_id)

        return jsonify({
            "message": "Product created successfully",
            "id": product.id
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# ============================================================
# GET ALL PRODUCTS
# ============================================================

@product_controller.route("", methods=["GET"])
@require_authentication
def get_products():

    user_id = g.user_id

    products = ProductService.get_all_products(user_id)

    return jsonify([
        serialize_product(product)
        for product in products
    ]), 200


# ============================================================
# GET PRODUCT BY ID
# ============================================================

@product_controller.route("/<int:product_id>", methods=["GET"])
@require_authentication
def get_product(product_id):

    user_id = g.user_id


    try:
        product = ProductService.get_product(product_id, user_id)

        return jsonify(serialize_product(product)), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404


# ============================================================
# UPDATE PRODUCT
# ============================================================

@product_controller.route("/<int:product_id>", methods=["PUT"])
@require_authentication
def update_product(product_id):

    user_id = g.user_id

    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body is required"}), 400

    try:
        product = ProductService.update_product(
            product_id,
            data,
            user_id
        )

        return jsonify({
            "message": "Product updated successfully",
            "id": product.id
        }), 200

    except ValueError as error:
        status_code = 404 if str(error) == "Product not found" else 400
        return jsonify({"error": str(error)}), status_code


# ============================================================
# DELETE PRODUCT
# ============================================================

@product_controller.route("/<int:product_id>", methods=["DELETE"])
@require_authentication
def delete_product(product_id):

    user_id = g.user_id

    try:
        ProductService.delete_product(product_id, user_id)

        return jsonify({
            "message": "Product deleted successfully"
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404


# ============================================================
# LOW STOCK PRODUCTS
# ============================================================

@product_controller.route("/low-stock", methods=["GET"])
@require_authentication
def get_low_stock_products():

    user_id = g.user_id

    products = ProductService.get_low_stock_products(user_id)

    return jsonify([
        serialize_product(product)
        for product in products
    ]), 200


# ============================================================
# SEARCH PRODUCTS
# ============================================================

@product_controller.route("/search", methods=["GET"])
@require_authentication
def search_products():

    user_id = g.user_id

    search = request.args.get("search")

    products = ProductService.search_products(search, user_id)

    return jsonify([
        serialize_product(product)
        for product in products
    ]), 200


# ============================================================
# FILTER BY CATEGORY
# ============================================================

@product_controller.route("/filter/category", methods=["GET"])
@require_authentication
def filter_products_by_category():

    user_id = g.user_id

    category_id = request.args.get("category_id", type=int)

    if category_id is None:
        return jsonify({"error": "Valid category_id is required"}), 400

    try:
        products = ProductService.filter_by_category(
            category_id,
            user_id
        )

        return jsonify([
            serialize_product(product)
            for product in products
        ]), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404


# ============================================================
# FILTER BY PRICE
# ============================================================

@product_controller.route("/filter/price", methods=["GET"])
@require_authentication
def filter_products_by_price():

    user_id = g.user_id

    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    try:
        products = ProductService.filter_by_price(
            user_id,
            min_price,
            max_price
        )

        return jsonify([
            serialize_product(product)
            for product in products
        ]), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# ============================================================
# FILTER BY STOCK
# ============================================================

@product_controller.route("/filter/stock", methods=["GET"])
@require_authentication
def filter_products_by_stock():

    user_id = g.user_id

    stock_status = request.args.get("stock_status")

    if not stock_status:
        return jsonify({"error": "stock_status is required"}), 400

    try:
        products = ProductService.filter_by_stock(
            stock_status,
            user_id
        )

        return jsonify([
            serialize_product(product)
            for product in products
        ]), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


# ============================================================
# SEARCH + FILTER + SORT + PAGINATION
# ============================================================

@product_controller.route("/browse", methods=["GET"])
@require_authentication
def browse_products():

    user_id = g.user_id
    
    search = request.args.get("search")

    category_id = request.args.get(
        "category_id",
        type=int
    )

    stock_status = request.args.get("stock_status")

    min_price = request.args.get("min_price", type=float)

    max_price = request.args.get("max_price", type=float)

    sort = request.args.get("sort", "created_at")

    order = request.args.get("order", "desc")

    page = request.args.get("page", 1, type=int)

    limit = request.args.get("limit", 10, type=int)

    try:
        pagination = ProductService.get_products(
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

        return jsonify({
            "data": [
                serialize_product(product)
                for product in pagination.items
            ],
            "pagination": {
                "page": pagination.page,
                "limit": pagination.per_page,
                "total_items": pagination.total,
                "total_pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev
            }
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
