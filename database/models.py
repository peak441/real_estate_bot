from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    telegram_id = db.Column(
        db.BigInteger,
        unique=True,
        nullable=False
    )

    username = db.Column(db.String(100))

    language = db.Column(
        db.String(10),
        default="en"
    )


class Property(db.Model):
    __tablename__ = "properties"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    property_type = db.Column(
        db.String(50)
    )

    price = db.Column(
        db.Float
    )

    bedrooms = db.Column(
        db.Integer
    )

    bathrooms = db.Column(
        db.Integer
    )

    size = db.Column(
        db.String(50)
    )

    location = db.Column(
        db.String(255)
    )

    province = db.Column(
        db.String(100)
    )

    latitude = db.Column(
        db.Float
    )

    longitude = db.Column(
        db.Float
    )

    status = db.Column(
        db.String(50),
        default="available"
    )


class PropertyImage(db.Model):
    __tablename__ = "property_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id")
    )

    image_url = db.Column(
        db.Text
    )

    is_thumbnail = db.Column(
        db.Boolean,
        default=False
    )


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id")
    )
class Inquiry(db.Model):
    __tablename__ = "inquiries"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    property_id = db.Column(
        db.Integer,
        db.ForeignKey("properties.id")
    )

    phone = db.Column(
        db.String(50)
    )

    message = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.now()
    )