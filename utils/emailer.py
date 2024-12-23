from email.mime.text import MIMEText
import os
import smtplib

SHOP_EMAIL = os.environ.get('SHOP_EMAIL')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT'))
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

def send_order_notification_email(order_details):
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

    send_email(subject, body, SHOP_EMAIL, EMAIL_USER)

def send_order_confirmation_email(order_details):
    subject = f"New Order Received: {order_details['paypal_order_id']}"
    body = (
        f"Your order has been placed!\n\n"
        f"Order ID: {order_details['paypal_order_id']}\n"
        f"Total Amount: ${order_details['total_amount']}\n\n"
        f"Items:\n"
    )
    for item in order_details['items']:
        body += f" - {item['name']}: ${item['price']}\n"

    send_email(subject, body, order_details['payer_email'], EMAIL_USER)

def send_email(subject, body, to_email, from_email):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Send the email via SMTP
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)