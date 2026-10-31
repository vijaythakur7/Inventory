from extensions import db


class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    sku = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    minimum_stock = db.Column(
        db.Integer,
        nullable=False,
        default=5
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    # Product owner (User Service ID)
    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now()
    )

    # Many Products → One Category
    category = db.relationship(
        "Category",
        back_populates="products"
    )

    # One Product → Many Stock Movements
    stock_movements = db.relationship(
        "StockMovement",
        back_populates="product",
        cascade="all, delete-orphan"
    )