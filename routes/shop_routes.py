import os

from flask import Blueprint, render_template

from models import Product

PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET')

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/store')
def store():
    # Fetch all active (non-discontinued) products from the database
    products = Product.query.filter_by(discontinued=False).all()
    return render_template('store.html', products=products, PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID)

@shop_bp.route('/shop/<int:item_id>')
def shop_item(item_id):
    # Query the database for the product by ID
    product = Product.query.get(item_id)

    # If the product is not found or discontinued, return a 404 page
    if not product or product.discontinued:
        return render_template('404.html'), 404

    return render_template('shop_item.html', product=product)