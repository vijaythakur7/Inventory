from flask import Blueprint, request, jsonify

from services.products_service import ProductService


product_controller = Blueprint(
    "product_controller",
    __name__,
    url_prefix="/api/products"
)


@product_controller.route("", methods=["POST"])
def create_product():

    data = request.get_json()

    try:

        product = ProductService.create_product(data)

        return jsonify({
            "message": "Product created successfully",
            "id": product.id
        }), 201

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 400


@product_controller.route("", methods=["GET"])
def get_products():

    products = ProductService.get_all_products()

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "quantity": product.quantity,
            "minimum_stock": product.minimum_stock,
            "category_id": product.category_id
        }
        for product in products
    ])


@product_controller.route(
    "/<int:product_id>",
    methods=["GET"]
)
def get_product(product_id):

    try:

        product = ProductService.get_product(
            product_id
        )

        return jsonify({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "price": float(product.price),
            "quantity": product.quantity,
            "minimum_stock": product.minimum_stock,
            "category_id": product.category_id
        })

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404


@product_controller.route(
    "/<int:product_id>",
    methods=["PUT"]
)
def update_product(product_id):

    data = request.get_json()

    try:

        product = ProductService.update_product(
            product_id,
            data
        )

        return jsonify({
            "message": "Product updated successfully",
            "id": product.id
        })

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404


@product_controller.route(
    "/<int:product_id>",
    methods=["DELETE"]
)
def delete_product(product_id):

    try:

        ProductService.delete_product(product_id)

        return jsonify({
            "message": "Product deleted successfully"
        })

    except ValueError as error:

        return jsonify({
            "error": str(error)
        }), 404


@product_controller.route(
    "/low-stock",
    methods=["GET"]
)
def get_low_stock_products():

    products = ProductService.get_low_stock_products()

    return jsonify([
        {
            "id": product.id,
            "name": product.name,
            "quantity": product.quantity,
            "minimum_stock": product.minimum_stock
        }
        for product in products
    ])