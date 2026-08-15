from datetime import date, timedelta
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required
from app.blueprints.products import products_bp
from app.blueprints.products.forms import ProductForm
from app.extensions import db
from app.models.product import Product
from app.services.product_service import generate_unique_slug, save_product_image, delete_product_image
from app.services.availability import get_available_quantity, get_booked_quantity


@products_bp.route('/')
@login_required
def index():
    """List active products with search, category filter, and pagination."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '', type=str).strip()
    category = request.args.get('category', '', type=str).strip()

    query = Product.query.filter(Product.is_active == True)  # noqa: E712

    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Product.category == category)

    query = query.order_by(Product.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    # Get distinct categories for filter dropdown (active products only)
    categories = db.session.query(Product.category).filter(
        Product.is_active == True,  # noqa: E712
        Product.category.isnot(None),
        Product.category != ''
    ).distinct().order_by(Product.category).all()
    category_list = [c[0] for c in categories]

    return render_template(
        'products/list.html',
        products=pagination.items,
        pagination=pagination,
        q=q,
        category=category,
        categories=category_list
    )


@products_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new product."""
    form = ProductForm()

    if form.validate_on_submit():
        slug = generate_unique_slug(form.name.data.strip())

        image_url = None
        if form.image.data:
            image_url = save_product_image(
                form.image.data,
                current_app.config['UPLOAD_FOLDER']
            )

        product = Product(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data or None,
            category=form.category.data.strip() if form.category.data else None,
            daily_rate=form.daily_rate.data,
            total_stock=form.total_stock.data,
            image_url=image_url
        )

        try:
            db.session.add(product)
            db.session.commit()
            flash(f"Product '{product.name}' created successfully.", 'success')
            return redirect(url_for('products.index'))
        except Exception:
            db.session.rollback()
            flash('An error occurred while creating the product. Please try again.', 'danger')

    return render_template('products/form.html', form=form, product=None)


@products_bp.route('/<int:id>')
@login_required
def detail(id):
    """Show product detail page with 30-day availability calendar."""
    product = Product.query.filter_by(id=id, is_active=True).first_or_404()

    today = date.today()
    availability_calendar = []
    for i in range(30):
        day = today + timedelta(days=i)
        avail = get_available_quantity(product.id, day, day)
        booked = get_booked_quantity(product.id, day, day)
        availability_calendar.append({
            'date': day,
            'available': avail,
            'booked': booked,
            'total': product.total_stock
        })

    return render_template(
        'products/detail.html',
        product=product,
        availability_calendar=availability_calendar
    )


@products_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing product."""
    product = Product.query.filter_by(id=id, is_active=True).first_or_404()
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        # Update slug if name changed
        if form.name.data.strip() != product.name:
            product.slug = generate_unique_slug(form.name.data.strip(), product_id=product.id)

        product.name = form.name.data.strip()
        product.description = form.description.data or None
        product.category = form.category.data.strip() if form.category.data else None
        product.daily_rate = form.daily_rate.data
        product.total_stock = form.total_stock.data

        # Handle image replacement: save new -> delete old -> update URL
        if form.image.data:
            new_image_url = save_product_image(
                form.image.data,
                current_app.config['UPLOAD_FOLDER']
            )
            if new_image_url:
                delete_product_image(product.image_url, current_app.config['UPLOAD_FOLDER'])
                product.image_url = new_image_url

        try:
            db.session.commit()
            flash(f"Product '{product.name}' updated successfully.", 'success')
            return redirect(url_for('products.detail', id=product.id))
        except Exception:
            db.session.rollback()
            flash('An error occurred while updating the product. Please try again.', 'danger')

    return render_template('products/form.html', form=form, product=product)


@products_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Soft-delete a product (set is_active = False)."""
    product = Product.query.filter_by(id=id, is_active=True).first_or_404()

    try:
        product.is_active = False
        db.session.commit()
        flash(f"Product '{product.name}' was deleted.", 'success')
    except Exception:
        db.session.rollback()
        flash('An error occurred while deleting the product. Please try again.', 'danger')

    return redirect(url_for('products.index'))
