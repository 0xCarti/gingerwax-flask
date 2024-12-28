
![Logo](https://gingerwax.ca/static/images/gingerwax_radio_min.png)


This is the official website for [Gingerwax](https://gingerwax.ca). The website encompassess art, e-commerce and storytelling. Gingerwax was founded back in 2014 by three individuals. Over the last decade the group has built art, ideas, lore, and a sense of unease...

## Roadmap

1. **Gingerwax Story Collection**

   - Integrate some sort of story/blog platform

2. **Create push notifications via email/sms**

   - Setup email verification
   - Setup sms verification
   - Create push notification data models

       - incoming order, new user register, new user activated, outgoing order, development issues
       - item restock, new item, item sold out, item discontinued
   - Edit user model to integrate push notifications
   - Create route/template to view/edit push notifications per user
   - Create a python module for notification related functions.

3. **Add coupon functionality to the store**

   - Create coupon models in the database

      - different types of coupons (fixed price, $ discount, % discount)
      - select items/item types to apply it to.
      - limit to X item(s) per order
   - Create route/template for adding/modifying a coupon.
   - Edit cart route to implement coupons
   - Edit cart template to re-calculate total based on coupon.
   - Edit order routes so they capture the coupon in the order details.


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

```bash
DATABASE_DIR=
PAYPAL_CLIENT_ID= [GET THIS FROM THE PAYPAL DEV PORTAL]
PAYPAL_SECRET= [GET THIS FROM THE PAYPAL DEV PORTAL]
FLASK_SECRET_KEY=SuperSecretKey1!
SHOP_EMAIL=youremail@email.com
EMAIL_HOST=smtp.mail.net
EMAIL_PORT=587
EMAIL_USER=smtp-email@mail.net
EMAIL_PASS=Password
TWILIO_ACCOUNT_SID= [GET THIS FROM THE TWILIO DEV PORTAL]
TWILIO_AUTH_TOKEN= [GET THIS FROM THE TWILIO DEV PORTAL]
MSG_SERVICE_ID= [GET THIS FROM THE TWILIO DEV PORTAL]
TWILIO_FROM_NUMBER= [GET THIS FROM THE TWILIO DEV PORTAL]
SHOP_CELL=+15555555
ADMIN_EMAIL=admin@email.com
ADMIN_PASSWORD=AdminPassword
```

## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Start the server (Development)

```bash
  python app.py
```




## Deployment (with Docker)

To deploy this project run

```bash
  docker run -p 5000:5000 --env-file .env gwcarti/gingerwax:latest
```

