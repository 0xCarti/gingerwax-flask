import os
from twilio.rest import Client

MSG_SERVICE_ID = os.environ.get('MSG_SERVICE_ID')
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')
SHOP_CELL = os.environ.get('SHOP_CELL')

def send_order_notification(order_details):
    body = (
        f"New order received!\n"
        f"Order ID: {order_details['paypal_order_id']}\n"
        f"Total: ${order_details['total_amount']}\n"
        f"Email: ${order_details['payer_email']}\n"
        "Better fuckin get on it!"
    )
    send_sms(body, SHOP_CELL)

def send_sms(body, to):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        messaging_service_sid=MSG_SERVICE_ID,
        body=body,
        to=to
    )