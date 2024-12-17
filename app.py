import os
from dotenv import load_dotenv
import requests
from flask import Flask, json, render_template, request, jsonify, session, render_template, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Set your PayPal credentials as environment variables or here directly
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET')
PAYPAL_OAUTH_URL = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
PAYPAL_ORDERS_URL = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
PRODUCTS_FILE = 'products.json'
ORDER_FILE = 'orders.json'
SHOP_EMAIL = os.environ.get('SHOP_EMAIL')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')
SHOP_CELL = os.environ.get('SHOP_CELL')

def send_order_email(order_details):
    # order_details is a dictionary containing order info
    # Build the email content from order_details
    subject = f"New Order Received: {order_details['paypal_order_id']}"
    body = (
        f"A new order has been placed.\n\n"
        f"Order ID: {order_details['paypal_order_id']}\n"
        f"Total Amount: ${order_details['total_amount']}\n\n"
        f"Items:\n"
    )
    for item in order_details['items']:
        body += f" - {item['name']}: ${item['price']}\n"

    body += "\nCustomer Info:\n"
    body += f"Name: {order_details.get('payer_given_name', '')} {order_details.get('payer_surname', '')}\n"
    body += f"Email: {order_details.get('payer_email', '')}\n"
    body += f"Phone: {order_details.get('payer_phone', '')}\n\n"
    body += "Shipping Address:\n"
    shipping = order_details.get('shipping_address', {})
    body += (
        f"{order_details.get('shipping_name', '')}\n"
        f"{shipping.get('address_line_1', '')}\n"
        f"{shipping.get('address_line_2', '')}\n"
        f"{shipping.get('admin_area_2', '')}, {shipping.get('admin_area_1', '')} {shipping.get('postal_code', '')}\n"
        f"{shipping.get('country_code', '')}\n"
    )

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = SHOP_EMAIL

    # Send the email via SMTP
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def get_paypal_access_token():
    response = requests.post(
        PAYPAL_OAUTH_URL,
        headers={"Accept": "application/json", "Accept-Language": "en_US"},
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )
    return response.json()['access_token']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store')
def store():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r') as f:
            products = json.load(f)
    else:
        products = []

    return render_template('store.html', products=products, PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    product_name = request.form.get('product_name')
    product_price = float(request.form.get('product_price'))

    # Initialize cart if not present
    if 'cart' not in session:
        session['cart'] = []

    # Add product to cart
    session['cart'].append({
        "id": product_id,
        "name": product_name,
        "price": product_price
    })
    session.modified = True
    return redirect(url_for('store'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total, PAYPAL_CLIENT_ID=PAYPAL_CLIENT_ID)

@app.route('/mmmm')
def mmmm():
    return render_template('mmmm.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create-order', methods=['POST'])
def create_order():
    access_token = get_paypal_access_token()
    cart = session.get('cart', [])

    # Calculate the total from the session cart
    total_amount = sum(item['price'] for item in cart)

    order = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "CAD",
                "value": f"{total_amount:.2f}"  # format as a string with two decimals
            }
        }]
    }

    response = requests.post(
        PAYPAL_ORDERS_URL,
        json=order,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )

    return jsonify(response.json())


@app.route('/capture-order', methods=['POST'])
def capture_order():
    import json
    import os
    from datetime import datetime

    access_token = get_paypal_access_token()
    data = request.get_json()
    order_id = data.get('orderID')
    capture_url = f"{PAYPAL_ORDERS_URL}/{order_id}/capture"
    response = requests.post(
        capture_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
    )
    order_data = response.json()

    if response.status_code == 201:
        cart = session.get('cart', [])
        total_amount = sum(item['price'] for item in cart)

        payer_info = order_data.get('payer', {})
        payer_email = payer_info.get('email_address')
        payer_given_name = payer_info.get('name', {}).get('given_name')
        payer_surname = payer_info.get('name', {}).get('surname')
        payer_phone = payer_info.get('phone_with_type', {}).get('phone_number', {}).get('national_number')

        purchase_unit = order_data['purchase_units'][0] if 'purchase_units' in order_data and len(order_data['purchase_units']) > 0 else {}
        shipping_info = purchase_unit.get('shipping', {})
        shipping_name = shipping_info.get('name', {}).get('full_name')
        shipping_address = shipping_info.get('address', {})

        new_order = {
            "paypal_order_id": order_data.get('id'),
            "total_amount": total_amount,
            "items": cart,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "payer_email": payer_email,
            "payer_given_name": payer_given_name,
            "payer_surname": payer_surname,
            "payer_phone": payer_phone,
            "shipping_name": shipping_name,
            "shipping_address": {
                "address_line_1": shipping_address.get('address_line_1'),
                "address_line_2": shipping_address.get('address_line_2'),
                "admin_area_1": shipping_address.get('admin_area_1'),
                "admin_area_2": shipping_address.get('admin_area_2'),
                "postal_code": shipping_address.get('postal_code'),
                "country_code": shipping_address.get('country_code')
            }
        }

        # Save order_data to JSON file
        orders_file = ORDER_FILE
        if os.path.exists(orders_file):
            with open(orders_file, 'r') as f:
                orders = json.load(f)
        else:
            orders = []

        orders.append(new_order)
        with open(orders_file, 'w') as f:
            json.dump(orders, f, indent=2)

        # Clear the cart
        session['cart'] = []

        # Send email notification
        #try:
            #send_order_email(new_order)
            #print("Email sent successfully")
        #except Exception as e:
            #print("Error sending email:", e)

        # Send SMS notification
        try:
            send_sms_notification(new_order)
            print("SMS sent successfully")
        except Exception as e:
            print("Error sending SMS:", e)

    return jsonify(order_data)




@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form.get('product_id')
    cart = session.get('cart', [])
    # Filter out the item with this product_id
    session['cart'] = [item for item in cart if str(item['id']) != product_id]
    return redirect(url_for('cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return redirect(url_for('cart'))

def send_sms_notification(order_details):
    # Construct the message body
    body = (
        f"New order received!\n"
        f"Order ID: {order_details['paypal_order_id']}\n"
        f"Total: ${order_details['total_amount']}\n"
        f"Email: ${order_details['payer_email']}\n"
        "Better fuckin get on it!"
    )
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        messaging_service_sid=os.environ.get('MSG_SERVICE_ID'),
        body=body,
        to='+12045731841'
    )
    print(message.sid)

if __name__ == '__main__':
    app.run(debug=True)
