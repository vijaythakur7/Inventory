from flask import Flask

from config.db_config import Config
from extensions import db
from extensions import db, migrate
from models.categories_model import Category
from models.products_model import Product
from models.stock_movements_model import StockMovement
# from controllers.book_controller import book_controller
from controllers.categories_controller import category_controller
from controllers.products_controller import product_controller
from controllers.stock_movements_controller import stock_controller

app = Flask(__name__)


# Database configuration
app.config.from_object(Config)


# Initialize SQLAlchemy
db.init_app(app)
migrate.init_app(app, db)


# Register Blueprint
# app.register_blueprint(book_controller)
app.register_blueprint(category_controller)
app.register_blueprint(product_controller)
app.register_blueprint(stock_controller)


# Create tables
with app.app_context():

    db.create_all()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)