from extensions import db


class StockMovement(db.Model):

    __tablename__ = "stock_movements"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id"),
        nullable=False
    )

    movement_type = db.Column(
        db.Enum("IN", "OUT"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    reason = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    # Many StockMovements → One Product
    product = db.relationship(
        "Product",
        back_populates="stock_movements"
    )