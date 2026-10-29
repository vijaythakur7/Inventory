from extensions import db

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    # One Category → Many Products
    products = db.relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan"
    )