from flask import Flask

from config.db_config import Config
from extensions import db, migrate

from models.categories_model import Category
from models.products_model import Product
from models.stock_movements_model import StockMovement

from controllers.categories_controller import category_controller
from controllers.products_controller import product_controller
from controllers.stock_movements_controller import stock_controller


def create_app(config_class=Config):

    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(category_controller)
    app.register_blueprint(product_controller)
    app.register_blueprint(stock_controller)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True
    )
