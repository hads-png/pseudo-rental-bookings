# Phase 2 — Product & Inventory Management

**Goal:** Full CRUD for products. Admin can add, view, edit, and soft-delete products. Product images can be uploaded.

## Tasks

- [x] **2.1** Create the **products blueprint** with routes:
  - `GET /products` — list all active products in a table/grid with columns: image thumbnail, name, category, daily rate, total stock, actions (edit/delete).
  - `GET /products/create` — render product form (empty).
  - `POST /products/create` — validate form, save product, redirect to product list.
  - `GET /products/<id>` — product detail page showing all info.
  - `GET /products/<id>/edit` — render product form (pre-filled).
  - `POST /products/<id>/edit` — validate, update product, redirect.
  - `POST /products/<id>/delete` — soft-delete (set `is_active = False`), redirect to list.
- [x] **2.2** Create `ProductForm` (Flask-WTF) with fields: name, description, category, daily_rate, total_stock, image (FileField).
- [x] **2.3** Implement image upload:
  - Save uploaded files to `app/static/uploads/` with a UUID filename to prevent collisions.
  - Store the relative path in `product.image_url`.
  - Validate file extension (allow: jpg, jpeg, png, webp only).
  - Set a max file size of 5MB in Flask config (`MAX_CONTENT_LENGTH`).
- [x] **2.4** Auto-generate the `slug` field from the product name using `slugify` (install `python-slugify`). Ensure uniqueness by appending a number if a duplicate exists.
- [x] **2.5** Add **search and filter** to the product list:
  - A search input that filters by product name (SQL `LIKE`).
  - A category dropdown filter.
  - Pagination (10 items per page) using Flask-SQLAlchemy's `paginate()`.
- [x] **2.6** Create the product list template (`products/list.html`) as a responsive table. On mobile, switch to a card layout using Tailwind breakpoints.
- [x] **2.7** Create the product detail template (`products/detail.html`) showing all product info, the image, and an "Edit" button.
- [x] **2.8** Create the shared form template (`products/form.html`) that handles both create and edit modes based on whether a product object is passed.

## Acceptance Criteria
- [x] Admin can create a product with an image, view it in the list, click into it, edit it, and soft-delete it.
- [x] Searching by name and filtering by category works.
- [x] Pagination works when there are more than 10 products.
- [x] Image uploads are saved to disk and display correctly.
