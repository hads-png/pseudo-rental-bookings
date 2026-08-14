"""
Product service layer — slug generation and image upload handling.
Business logic lives here, not in route handlers (Section 9, Convention #3).
"""
import os
import uuid

from slugify import slugify
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.product import Product


def generate_unique_slug(name: str, product_id: int | None = None) -> str:
    """Generate a unique URL-friendly slug from a product name.

    Queries ALL products (active and inactive) because the slug column
    has a UNIQUE constraint at the database level. Appends sequential
    suffixes (-1, -2, ...) to resolve collisions.

    Args:
        name: The product name to slugify.
        product_id: If editing, exclude this product's own slug from collision checks.

    Returns:
        A unique slug string.
    """
    base_slug = slugify(name, max_length=170)
    candidate = base_slug
    counter = 1

    while True:
        query = Product.query.filter(Product.slug == candidate)
        if product_id is not None:
            query = query.filter(Product.id != product_id)
        if query.first() is None:
            return candidate
        candidate = f"{base_slug}-{counter}"
        counter += 1


def save_product_image(file_storage, upload_folder: str) -> str | None:
    """Save an uploaded image file with a UUID-based filename.

    Args:
        file_storage: A Werkzeug FileStorage object from the form.
        upload_folder: Absolute path to the uploads directory.

    Returns:
        Relative web path (e.g. 'uploads/abc123.jpg') for DB storage,
        or None if no valid file was provided.
    """
    if file_storage is None or file_storage.filename == '':
        return None

    original_filename = secure_filename(file_storage.filename)
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''

    if not ext:
        return None

    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    os.makedirs(upload_folder, exist_ok=True)
    file_storage.save(os.path.join(upload_folder, unique_filename))

    return f"uploads/{unique_filename}"


def delete_product_image(image_url: str | None, upload_folder: str) -> None:
    """Delete a product image file from disk.

    Args:
        image_url: The relative web path stored in product.image_url.
        upload_folder: Absolute path to the uploads directory.
    """
    if not image_url:
        return

    filename = image_url.replace('uploads/', '', 1)
    filepath = os.path.join(upload_folder, filename)

    if os.path.isfile(filepath):
        os.remove(filepath)
