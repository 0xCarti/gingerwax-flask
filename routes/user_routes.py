
from flask import Blueprint, app
from flask import flash, request, render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from models import db, User

user_bp = Blueprint('user', __name__)

login_manager.login_view = 'user.login'  # Redirect to this route if not logged in
login_manager.login_message = "Please log in to access this page."

@user_bp.route('/admin/users')
@login_required
def admin_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@user_bp.route('/admin/users/activate/<int:user_id>', methods=['POST'])
@login_required
def activate_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = True
        db.session.commit()
        flash(f"User {user.email} activated successfully.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('user.admin_users'))

@user_bp.route('/admin/users/deactivate/<int:user_id>', methods=['POST'])
@login_required
def deactivate_user(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_active = False
        db.session.commit()
        flash(f"User {user.email} deactivated successfully.", "success")
    else:
        flash("User not found.", "danger")
    return redirect(url_for('user.admin_users'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_active:
                login_user(user)
                flash("Login successful!", "success")
                return redirect(url_for('admin.admin_dashboard'))  # Redirect to the dashboard
            else:
                flash("Your account is not activated. Please contact the admin.", "warning")
        else:
            flash("Invalid email or password.", "danger")
    return render_template('login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Route for adding users
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User with this email already exists.", "danger")
            return redirect(url_for('register'))

        # Create new user
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(email=email, password_hash=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("User registered successfully!", "success")
        return redirect(url_for('register'))

    return render_template('register.html')