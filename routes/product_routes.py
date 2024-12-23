import os
import uuid

from PIL import Image
from flask import Blueprint, app, render_template, flash, redirect, url_for, request
from flask_login import login_required

from app import db
from models import Product

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'avif'}
UPLOAD_FOLDER = 'static/images'

product_bp = Blueprint('product', __name__)

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()  # Extract file extension
    unique_id = uuid.uuid4().hex  # Generate unique identifier
    return f"{unique_id}.{ext}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for('admin.admin_products'))

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.short_description = request.form.get('short_description')
        product.long_description = request.form.get('long_description')
        
        stock_input = request.form.get('stock')
        product.stock = int(stock_input) if stock_input else None

        # Handle optional file upload
        file = request.files['image']
        if file and allowed_file(file.filename):
            unique_filename = generate_unique_filename(file.filename)
            base_name, ext = os.path.splitext(unique_filename)

            full_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_full{ext}")
            file.save(full_path)

            shop_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_shop{ext}")
            with Image.open(full_path) as img:
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                img.save(shop_path)

            min_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_min{ext}")
            with Image.open(full_path) as img:
                img.save(min_path, optimize=True, quality=20)

            product.full_image_link = f"/static/images/{base_name}_full{ext}"

        db.session.commit()
        flash(f"Product '{product.name}' updated successfully.", "success")
        return redirect(url_for('admin.admin_products'))

    return render_template('edit_product.html', product=product)

@product_bp.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        price = float(request.form.get('price'))
        short_description = request.form.get('short_description')
        long_description = request.form.get('long_description')

        stock_input = request.form.get('stock')
        stock = int(stock_input) if stock_input else None  # Allow empty stock field

        # Handle file upload
        file = request.files['image']
        if file and allowed_file(file.filename):
            unique_filename = generate_unique_filename(file.filename)
            base_name, ext = os.path.splitext(unique_filename)

            # Save original as "filename_full"
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_full{ext}")
            file.save(full_path)

            # Resize and save other versions
            shop_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_shop{ext}")
            with Image.open(full_path) as img:
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                img.save(shop_path)

            min_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{base_name}_min{ext}")
            with Image.open(full_path) as img:
                img.save(min_path, optimize=True, quality=20)

            # Only save filenames in the database, not the full path
            full_image_link = f"{base_name}_full{ext}"
        else:
            flash("Invalid image file. Please upload a valid PNG, JPG, AVIF, or WEBP image.", "danger")
            return redirect(url_for('admin.add_product'))

        # Create and save the new product
        new_product = Product(
            name=name,
            price=price,
            short_description=short_description,
            long_description=long_description,
            stock=stock,
            full_image_link=full_image_link
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f"Product '{name}' added successfully.", "success")
        return redirect(url_for('admin.admin_products'))

    return render_template('add_product.html')

@product_bp.route('/admin/products', methods=['GET'])
@login_required
def admin_products():
    search_query = request.args.get('search', '').strip()

    if search_query:
        # Filter products by name or short description and exclude discontinued products
        products = Product.query.filter(
            (Product.name.ilike(f"%{search_query}%")) |
            (Product.short_description.ilike(f"%{search_query}%")),
            Product.discontinued == False
        ).all()
    else:
        # Fetch all active products (not discontinued) if no search query
        products = Product.query.filter_by(discontinued=False).all()

    return render_template('admin_products.html', products=products)



@product_bp.route('/admin/products/all')
@login_required
def admin_all_products():
    products = Product.query.all()  # Include discontinued products
    return render_template('admin_products.html', products=products)


@product_bp.route('/admin/products/discontinue/<int:product_id>', methods=['POST'])
@login_required
def discontinue_product(product_id):
    product = Product.query.get(product_id)
    if product:
        product.discontinued = True
        db.session.commit()
        flash(f"Product '{product.short_description}' marked as discontinued.", "success")
    else:
        flash("Product not found.", "danger")
    return redirect(url_for('admin.admin_products'))