from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required

from app import db
from models import Order

order_bp = Blueprint('order', __name__)

@order_bp.route('/admin/orders', methods=['GET', 'POST'])
@login_required
def admin_orders():
    if request.method == 'POST':
        order_id = request.form.get('order_id')
        order = Order.query.get(order_id)
        if order:
            order.completed = True
            db.session.commit()
            flash(f"Order #{order.id} marked as completed.", "success")
        else:
            flash("Order not found.", "danger")

    orders = Order.query.order_by(Order.date.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@order_bp.route('/admin/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        if not order.completed:
            order.completed = True
            db.session.commit()
            flash(f"Order #{order.id} marked as completed.", "success")
        return redirect(url_for('order.view_order', order_id=order.id))

    return render_template('view_order.html', order=order)

