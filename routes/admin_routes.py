from flask import Blueprint, render_template
from flask_login import login_required

from models import Order, Statistics

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'avif'}
UPLOAD_FOLDER = 'static/images'

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # Count pending and completed orders based on the 'completed' column
    pending_orders = Order.query.filter_by(completed=False).count()
    completed_orders = Order.query.filter_by(completed=True).count()

    # Get site visits from the Statistics model
    site_visits = Statistics.query.first().site_visits if Statistics.query.first() else 0

    return render_template(
        'dashboard.html',
        pending_orders=pending_orders,
        completed_orders=completed_orders,
        site_visits=site_visits
    )