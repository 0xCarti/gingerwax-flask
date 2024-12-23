from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the database (to be initialized in app.py)
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    orders = db.relationship('Order', back_populates='user', lazy=True)  # Relationship to Order


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    full_image_link = db.Column(db.String(200), nullable=True)
    stock = db.Column(db.Integer, nullable=True, default=0)  # Optional stock
    short_description = db.Column(db.String(255), nullable=False)
    long_description = db.Column(db.Text, nullable=True)
    discontinued = db.Column(db.Boolean, default=False)

    def is_unlimited_stock(self):
        return self.stock == -1


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique Order Number
    date = db.Column(db.DateTime, default=datetime.utcnow)  # Order date and time
    customer_email = db.Column(db.String(120), nullable=False)  # Customer email
    total_amount = db.Column(db.Float, nullable=False)  # Total price of the order
    completed = db.Column(db.Boolean, default=False)  # Order status
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Foreign key to User table
    shipping_name = db.Column(db.String(255), nullable=True)  # Shipping name
    shipping_address_line_1 = db.Column(db.String(255), nullable=True)  # Address line 1
    shipping_address_line_2 = db.Column(db.String(255), nullable=True)  # Address line 2 (optional)
    shipping_city = db.Column(db.String(100), nullable=True)  # City
    shipping_state = db.Column(db.String(100), nullable=True)  # State or province
    shipping_postal_code = db.Column(db.String(20), nullable=True)  # Postal or ZIP code
    shipping_country = db.Column(db.String(100), nullable=True)  # Country
    paypal_order_id = db.Column(db.String(255), nullable=False)  # PayPal order ID

    user = db.relationship('User', back_populates='orders')  # Relationship to User
    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")  # Relationship to OrderItem


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', back_populates='items')  # Relationship to Order
    product = db.relationship('Product')  # Relationship to Product

class Statistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_visits = db.Column(db.Integer, default=0)

    @staticmethod
    def increment_visits():
        stats = Statistics.query.first()
        if not stats:
            stats = Statistics(site_visits=1)
            db.session.add(stats)
        else:
            stats.site_visits += 1
        db.session.commit()
        return stats.site_visits