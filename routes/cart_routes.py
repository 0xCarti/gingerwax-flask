from flask import Blueprint, render_template, flash, redirect, session, url_for, request

from models import Product
from routes.shop_routes import PAYPAL_CLIENT_ID

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')
    cart = session.get('cart', [])
    # Filter out the item with this product_id
    session['cart'] = [item for item in cart if str(item['id']) != product_id]
    return redirect(url_for('cart.cart'))

@cart_bp.route('/clear_cart', methods=['POST', 'GET'])
def clear_cart():
    session['cart'] = []
    return redirect(url_for('cart.cart'))

@cart_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    if not product_id:
        flash("Product ID is missing.", "danger")
        return redirect(url_for('store.store'))

    # Fetch product from the database
    product = Product.query.get(product_id)
    if not product or product.discontinued:
        flash("Product is not available.", "danger")
        return redirect(url_for('store.store'))

    quantity = int(request.form.get('quantity', 1))  # Default quantity to 1

    # Initialize cart if not present
    if 'cart' not in session:
        session['cart'] = []

    # Ensure product_id is included when adding to the cart
    for item in session['cart']:
        if item['id'] == product.id:
            item['quantity'] += quantity
            session.modified = True
            flash(f"Updated {product.name} quantity in cart.", "success")
            return redirect(url_for('store.store'))

    session['cart'].append({
        "product_id": product.id,  # Always include product_id
        "name": product.name,
        "price": product.price,
        "image_min": product.full_image_link.replace('_full', '_min') if '_full' in product.full_image_link else product.full_image_link,
        "quantity": quantity
    })
    session.modified = True
    flash(f"{product.name} added to cart.", "success")
    return redirect(url_for('store.store'))


@cart_bp.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total, PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID)