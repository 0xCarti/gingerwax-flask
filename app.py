import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
from flask_login import LoginManager
from flask_migrate import Migrate # type: ignore
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash

from models import Statistics
from models import db, User
from routes.admin_routes import UPLOAD_FOLDER, admin_bp
from routes.cart_routes import cart_bp
from routes.order_routes import order_bp
from routes.product_routes import product_bp
from routes.shop_routes import shop_bp

load_dotenv()  # Load variables from .env file

# Create the database directory if it doesn't exist
DATABASE_DIR = os.getenv("DATABASE_DIR", "")
if len(DATABASE_DIR) > 0:
    os.makedirs(DATABASE_DIR, exist_ok=True)  # Ensure the directory exists

# Setup the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Explicitly configure the environment
app.config["ENV"] = os.getenv("FLASK_ENV", "production")
app.config["DEBUG"] = app.config["ENV"] == "development"

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(DATABASE_DIR, 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

csrf = CSRFProtect(app) # Enable CSRF protection 

# Initialize the database and migration engine
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app) # Setup the login manager

# Function to auto-create a admin account for intial setup of further user accounts.
def create_admin_account():
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')

    if admin_email and admin_password:
        with app.app_context():
            existing_admin = User.query.filter_by(email=admin_email).first()
            if not existing_admin:
                hashed_password = generate_password_hash(admin_password, method='sha256')
                admin = User(
                    email=admin_email,
                    password_hash=hashed_password,
                    is_admin=True,
                    is_active=True  # Admin is always active
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin account created.")
            else:
                print("Admin account already exists.")
    else:
        print("Admin email and password not set in .env.")

with app.app_context():
    db.create_all()
    create_admin_account()

@app.before_request
def increment_site_visits():
    with app.app_context():
        Statistics.increment_visits()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mmmm')
def mmmm():
    return render_template('mmmm.html')

@app.route('/about')
def about():
    return render_template('about.html')

from routes.transaction_routes import transaction_bp
from routes.user_routes import user_bp

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(user_bp)
app.register_blueprint(order_bp)
app.register_blueprint(product_bp)

if __name__ == '__main__':
    app.run(debug=app.config["DEBUG"])
