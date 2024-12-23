from email.mime.text import MIMEText
import os

import requests
from flask import Blueprint, current_app, jsonify, session, request, url_for
from flask_login import current_user

from app import db, csrf
from models import Order, OrderItem, Product
from routes.shop_routes import PAYPAL_CLIENT_ID, PAYPAL_SECRET
from utils.emailer import send_digital_order_email, send_order_confirmation_email, send_order_notification_email

# Set your PayPal credentials as environment variables or here directly
#PAYPAL_OAUTH_URL = "https://api-m.paypal.com/v1/oauth2/token"
#PAYPAL_ORDERS_URL = "https://api-m.paypal.com/v2/checkout/orders"
PAYPAL_OAUTH_URL = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
PAYPAL_ORDERS_URL = "https://api-m.sandbox.paypal.com/v2/checkout/orders"

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/create-order', methods=['POST'])
@csrf.exempt
def create_order():
    try:
        # Generate PayPal access token
        access_token = get_paypal_access_token()

        # Fetch the cart from session
        cart = session.get('cart', [])
        if not cart:
            return jsonify({"error": "Cart is empty"}), 400

        # Calculate the total amount
        total_amount = sum(item['price'] * item.get('quantity', 1) for item in cart)

        # Prepare the PayPal order payload
        order = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": "CAD",
                        "value": f"{total_amount:.2f}"  # Ensure two decimal places
                    }
                }
            ]
        }

        # Send the order to PayPal
        response = requests.post(
            PAYPAL_ORDERS_URL,
            json=order,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        response.raise_for_status()

        # Parse and return the PayPal response
        order_data = response.json()
        return jsonify({"orderID": order_data["id"]})

    except requests.exceptions.RequestException as e:
        print(f"Error creating PayPal order: {e}")
        return jsonify({"error": "Failed to create PayPal order", "details": str(e)}), 500

    except Exception as e:
        print(f"Unexpected error in create_order: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@transaction_bp.route('/capture-order', methods=['POST'])
@csrf.exempt
def capture_order():
    try:
        access_token = get_paypal_access_token()

        data = request.get_json()
        order_id = data.get('orderID')
        if not order_id:
            return jsonify({"error": "Missing orderID"}), 400

        capture_url = f"{PAYPAL_ORDERS_URL}/{order_id}/capture"
        response = requests.post(
            capture_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )
        if response.status_code != 201:
            print(f"Error capturing PayPal order: {response.text}")
            return jsonify({"error": "Failed to capture order", "details": response.text}), response.status_code

        order_data = response.json()
        cart = session.get('cart', [])
        if not cart:
            return jsonify({"error": "Cart is empty"}), 400
        

        total_amount = sum(item['price'] * item.get('quantity', 1) for item in cart)

        # Create the Order in the database
        new_order = Order(
            customer_email=order_data.get('payer', {}).get('email_address', ''),
            total_amount=total_amount,
            completed=False,
            paypal_order_id=order_data.get('id'),  # Save PayPal order ID
            user_id=current_user.id if current_user.is_authenticated else None,
            shipping_name=order_data['purchase_units'][0]['shipping']['name']['full_name'],
            shipping_address_line_1=order_data['purchase_units'][0]['shipping']['address']['address_line_1'],
            shipping_address_line_2=order_data['purchase_units'][0]['shipping']['address'].get('address_line_2', ''),
            shipping_city=order_data['purchase_units'][0]['shipping']['address']['admin_area_2'],
            shipping_state=order_data['purchase_units'][0]['shipping']['address']['admin_area_1'],
            shipping_postal_code=order_data['purchase_units'][0]['shipping']['address']['postal_code'],
            shipping_country=order_data['purchase_units'][0]['shipping']['address']['country_code']
        )
        db.session.add(new_order)
        db.session.commit()

        # Add items to the OrderItem table and reduce stock
        for item in cart:
            if 'id' not in item:
                print(f"Invalid cart item: {item}")
                return jsonify({"error": f"Invalid cart item: {item}"}), 400

            # Find the product in the database
            product = Product.query.get(item['id'])
            if not product:
                print(f"Product not found for ID {item['id']}")
                return jsonify({"error": f"Product not found for ID {item['id']}"}), 400

            # Check if the product has sufficient stock
            if not product.is_unlimited_stock() and product.stock < item.get('quantity', 1):
                print(f'Insufficient stock for product {product.name}')
                return jsonify({"error": f"Insufficient stock for product {product.name}"}), 400

            # Reduce stock if applicable
            if not product.is_unlimited_stock():
                product.stock -= item.get('quantity', 1)

            # Create an OrderItem
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=item.get('quantity', 1),
                price=item['price']
            )
            db.session.add(order_item)

        db.session.commit()
        session['cart'] = []

        # Send confirmation email
        order_details = {
            "paypal_order_id": new_order.paypal_order_id,
            "total_amount": new_order.total_amount,
            "items": [
                {
                    "name": item.product.name,
                    "price": item.price,
                    "quantity": item.quantity
                }
                for item in new_order.items
            ],
            "payer_email": new_order.customer_email
        }
        
        for item in cart:
            product = Product.query.get(item['id'])
            if product.type == "Physical":
                send_order_notification_email(order_details)
            elif product.type == "Digital":
                # Generate the absolute file system path
                image_path = os.path.join(current_app.root_path, 'static', 'images', os.path.basename(product.full_image_link))
                if os.path.exists(image_path):
                    send_digital_order_email(order_details, image_path)
                else:
                    raise FileNotFoundError(f"Digital goods file not found: {image_path}")

        return jsonify(order_data)

    except Exception as e:
        print(f"Unexpected error in capture_order: {e}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


def get_paypal_access_token():
    response = requests.post(
        PAYPAL_OAUTH_URL,
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )
    return response.json()['access_token']