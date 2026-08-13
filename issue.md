# Pseudo Booqable — Rental Booking System

> **Project Type:** Personal / Learning Project  
> **Stack:** Python 3.12 · Flask · MySQL · TailwindCSS 3.3  
> **Inspired by:** [Booqable](https://booqable.com) rental management software

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack & Environment](#2-tech-stack--environment)
3. [Database Schema](#3-database-schema)
4. [Application Structure](#4-application-structure)
5. [Implementation Phases](#5-implementation-phases)
   - [Phase 1 — Project Scaffolding & Auth](#phase-1--project-scaffolding--auth)
   - [Phase 2 — Product & Inventory Management](#phase-2--product--inventory-management)
   - [Phase 3 — Customer Management](#phase-3--customer-management)
   - [Phase 4 — Orders & Booking Engine](#phase-4--orders--booking-engine)
   - [Phase 5 — Availability Engine](#phase-5--availability-engine)
   - [Phase 6 — Invoicing & Payments](#phase-6--invoicing--payments)
   - [Phase 7 — Dashboard & Reporting](#phase-7--dashboard--reporting)
   - [Phase 8 — Polish, Settings & Deployment](#phase-8--polish-settings--deployment)
6. [UI/UX Guidelines](#6-uiux-guidelines)
7. [API Route Map](#7-api-route-map)
8. [Testing Strategy](#8-testing-strategy)
9. [Conventions & Rules](#9-conventions--rules)

---

## 1. Project Overview

**Pseudo Booqable** is a simplified clone of the Booqable rental management platform. It allows a business owner (the **admin/staff**) to:

- Manage a catalog of **rental products** (e.g., cameras, power tools, party equipment).
- Track **inventory stock** per product — how many units exist, how many are currently rented out, and how many are available.
- Manage **customers** — store contact details and view their rental history.
- Create and manage **orders** (bookings) — each order ties a customer to one or more products for a specific date range.
- Automatically calculate **availability** so that products cannot be double-booked.
- Generate simple **invoices** for each order.
- View a **dashboard** with key metrics (active orders, revenue, popular products).

### What This Project Is NOT

- Not a public-facing online storefront (no customer self-service portal in v1).
- Not a payment gateway integration (invoices are generated but payments are recorded manually).
- Not a multi-tenant SaaS (single business / single admin).

---

## 2. Tech Stack & Environment

| Layer        | Technology                | Version / Notes                                     |
|:-------------|:--------------------------|:----------------------------------------------------|
| Language     | Python                    | 3.12                                                |
| Web Framework| Flask                     | Latest stable (use `flask[async]` if needed)        |
| Database     | MySQL                     | 8.x recommended                                     |
| ORM          | Flask-SQLAlchemy           | Use SQLAlchemy 2.x style (mapped classes)           |
| Migrations   | Flask-Migrate (Alembic)    | All schema changes via migrations, never raw DDL    |
| Auth         | Flask-Login                | Session-based authentication                        |
| Forms        | Flask-WTF                  | Server-side form validation                         |
| CSS          | TailwindCSS               | **3.3** — installed via Node/npm, built via CLI     |
| Templating   | Jinja2                    | Built into Flask                                    |
| Environment  | python-dotenv              | `.env` file for secrets and config                  |

### Environment Setup Instructions

> **For the implementer:** Follow these steps exactly when first setting up the project.

1. **Create a Python virtual environment:**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

2. **Install Python dependencies:**
   ```bash
   pip install flask flask-sqlalchemy flask-migrate flask-login flask-wtf pymysql python-dotenv email-validator
   pip freeze > requirements.txt
   ```

3. **Initialize Node.js & TailwindCSS 3.3:**
   ```bash
   npm init -y
   npm install -D tailwindcss@3.3
   npx tailwindcss init
   ```

4. **Configure `tailwind.config.js`:**
   ```js
   /** @type {import('tailwindcss').Config} */
   module.exports = {
     content: ["./app/templates/**/*.html", "./app/static/js/**/*.js"],
     theme: {
       extend: {},
     },
     plugins: [],
   };
   ```

5. **Create a source CSS file at `app/static/css/input.css`:**
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

6. **Add an npm script in `package.json`:**
   ```json
   "scripts": {
     "css:build": "npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css",
     "css:watch": "npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css --watch"
   }
   ```

7. **Create a `.env` file (never commit this):**
   ```dotenv
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=change-me-to-a-random-string
   DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/pseudo_booqable
   ```

8. **Create the MySQL database:**
   ```sql
   CREATE DATABASE pseudo_booqable CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

---

## 3. Database Schema

> **For the implementer:** Translate each table below into a SQLAlchemy model class. Every model MUST include `id` (primary key), `created_at`, and `updated_at` timestamp columns.

### Entity Relationship Diagram (Conceptual)

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│   User   │       │   Product    │       │ Customer │
│ (admin)  │       │              │       │          │
└──────────┘       └──────┬───────┘       └────┬─────┘
                          │                     │
                          │ 1:N                 │ 1:N
                          ▼                     ▼
                   ┌──────────────┐      ┌───────────┐
                   │ ProductStock │      │   Order   │
                   │  (units)     │      │           │
                   └──────────────┘      └─────┬─────┘
                                               │
                                               │ 1:N
                                               ▼
                                        ┌─────────────┐
                                        │  OrderItem  │
                                        │(product+qty)│
                                        └─────────────┘
```

### Table Definitions

#### `users`
| Column          | Type           | Constraints                  | Notes                        |
|:----------------|:---------------|:-----------------------------|:-----------------------------|
| id              | INT            | PK, AUTO_INCREMENT           |                              |
| username        | VARCHAR(80)    | UNIQUE, NOT NULL             |                              |
| email           | VARCHAR(120)   | UNIQUE, NOT NULL             |                              |
| password_hash   | VARCHAR(256)   | NOT NULL                     | Use `werkzeug.security`      |
| is_active       | BOOLEAN        | DEFAULT TRUE                 |                              |
| created_at      | DATETIME       | DEFAULT CURRENT_TIMESTAMP    |                              |
| updated_at      | DATETIME       | ON UPDATE CURRENT_TIMESTAMP  |                              |

#### `products`
| Column          | Type           | Constraints                  | Notes                                  |
|:----------------|:---------------|:-----------------------------|:---------------------------------------|
| id              | INT            | PK, AUTO_INCREMENT           |                                        |
| name            | VARCHAR(150)   | NOT NULL                     |                                        |
| slug            | VARCHAR(170)   | UNIQUE, NOT NULL             | Auto-generated from name               |
| description     | TEXT           | NULLABLE                     |                                        |
| image_url       | VARCHAR(500)   | NULLABLE                     | Path to uploaded image                 |
| daily_rate      | DECIMAL(10,2)  | NOT NULL                     | Price per day                          |
| total_stock     | INT            | NOT NULL, DEFAULT 0          | Total number of physical units owned   |
| category        | VARCHAR(100)   | NULLABLE                     | Simple string category for now         |
| is_active       | BOOLEAN        | DEFAULT TRUE                 | Soft-delete / hide from booking        |
| created_at      | DATETIME       | DEFAULT CURRENT_TIMESTAMP    |                                        |
| updated_at      | DATETIME       | ON UPDATE CURRENT_TIMESTAMP  |                                        |

#### `customers`
| Column          | Type           | Constraints                  | Notes                        |
|:----------------|:---------------|:-----------------------------|:-----------------------------|
| id              | INT            | PK, AUTO_INCREMENT           |                              |
| first_name      | VARCHAR(80)    | NOT NULL                     |                              |
| last_name       | VARCHAR(80)    | NOT NULL                     |                              |
| email           | VARCHAR(120)   | UNIQUE, NOT NULL             |                              |
| phone           | VARCHAR(30)    | NULLABLE                     |                              |
| address         | TEXT           | NULLABLE                     |                              |
| notes           | TEXT           | NULLABLE                     | Internal notes about customer|
| created_at      | DATETIME       | DEFAULT CURRENT_TIMESTAMP    |                              |
| updated_at      | DATETIME       | ON UPDATE CURRENT_TIMESTAMP  |                              |

#### `orders`
| Column          | Type           | Constraints                  | Notes                                   |
|:----------------|:---------------|:-----------------------------|:----------------------------------------|
| id              | INT            | PK, AUTO_INCREMENT           |                                         |
| order_number    | VARCHAR(20)    | UNIQUE, NOT NULL             | Auto-generated (e.g., `ORD-20260813-001`)|
| customer_id     | INT            | FK → customers.id, NOT NULL  |                                         |
| status          | VARCHAR(20)    | NOT NULL, DEFAULT 'draft'    | Enum: `draft`, `confirmed`, `picked_up`, `returned`, `cancelled` |
| rental_start    | DATE           | NOT NULL                     |                                         |
| rental_end      | DATE           | NOT NULL                     | Must be ≥ rental_start                  |
| subtotal        | DECIMAL(10,2)  | NOT NULL, DEFAULT 0          | Sum of all order_items                  |
| discount        | DECIMAL(10,2)  | DEFAULT 0                    |                                         |
| tax_rate        | DECIMAL(5,4)   | DEFAULT 0                    | e.g., 0.1000 = 10%                     |
| total           | DECIMAL(10,2)  | NOT NULL, DEFAULT 0          | (subtotal - discount) × (1 + tax_rate) |
| notes           | TEXT           | NULLABLE                     |                                         |
| created_at      | DATETIME       | DEFAULT CURRENT_TIMESTAMP    |                                         |
| updated_at      | DATETIME       | ON UPDATE CURRENT_TIMESTAMP  |                                         |

#### `order_items`
| Column          | Type           | Constraints                           | Notes                                      |
|:----------------|:---------------|:--------------------------------------|:-------------------------------------------|
| id              | INT            | PK, AUTO_INCREMENT                    |                                            |
| order_id        | INT            | FK → orders.id, NOT NULL, ON DELETE CASCADE |                                      |
| product_id      | INT            | FK → products.id, NOT NULL            |                                            |
| quantity         | INT            | NOT NULL, DEFAULT 1                   | Must be ≥ 1                                |
| daily_rate      | DECIMAL(10,2)  | NOT NULL                              | Snapshot of product rate at time of booking |
| line_total      | DECIMAL(10,2)  | NOT NULL                              | quantity × daily_rate × number_of_days     |
| created_at      | DATETIME       | DEFAULT CURRENT_TIMESTAMP             |                                            |

---

## 4. Application Structure

> **For the implementer:** Create this exact folder structure. Use Flask Blueprints to organize routes. Each feature area gets its own blueprint.

```
pseudo-booqable/
├── run.py                      # Entry point: creates and runs the app
├── config.py                   # App configuration (reads from .env)
├── .env                        # Environment variables (DO NOT COMMIT)
├── .gitignore
├── requirements.txt
├── package.json
├── tailwind.config.js
│
├── app/
│   ├── __init__.py             # App factory: create_app()
│   ├── extensions.py           # Initialize db, migrate, login_manager
│   ├── models/
│   │   ├── __init__.py         # Import all models here
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── customer.py
│   │   ├── order.py
│   │   └── order_item.py
│   │
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py     # Blueprint registration
│   │   │   ├── routes.py       # Login, logout, register
│   │   │   └── forms.py       # LoginForm, RegisterForm
│   │   ├── dashboard/
│   │   │   ├── __init__.py
│   │   │   └── routes.py       # Dashboard home page
│   │   ├── products/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py       # CRUD routes for products
│   │   │   └── forms.py
│   │   ├── customers/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py       # CRUD routes for customers
│   │   │   └── forms.py
│   │   ├── orders/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py       # CRUD routes for orders
│   │   │   └── forms.py
│   │   └── invoices/
│   │       ├── __init__.py
│   │       └── routes.py       # Invoice generation and viewing
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── availability.py     # Availability checking logic
│   │   ├── order_service.py    # Order totals calculation
│   │   └── invoice_service.py  # Invoice generation
│   │
│   ├── static/
│   │   ├── css/
│   │   │   ├── input.css       # TailwindCSS source
│   │   │   └── output.css      # TailwindCSS compiled (git-ignored)
│   │   ├── js/
│   │   │   └── app.js          # Minimal JS (date pickers, modals, etc.)
│   │   └── uploads/            # Product images
│   │
│   └── templates/
│       ├── base.html           # Master layout (nav, sidebar, footer)
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── dashboard/
│       │   └── index.html
│       ├── products/
│       │   ├── list.html
│       │   ├── detail.html
│       │   └── form.html       # Shared create/edit form
│       ├── customers/
│       │   ├── list.html
│       │   ├── detail.html
│       │   └── form.html
│       ├── orders/
│       │   ├── list.html
│       │   ├── detail.html
│       │   └── form.html
│       ├── invoices/
│       │   └── detail.html     # Printable invoice page
│       └── components/
│           ├── _navbar.html
│           ├── _sidebar.html
│           ├── _flash_messages.html
│           ├── _pagination.html
│           └── _confirm_modal.html
│
└── migrations/                 # Auto-generated by Flask-Migrate
```

### Key Architecture Decisions

| Decision | Rationale |
|:---------|:----------|
| **App Factory pattern** (`create_app()`) | Standard Flask best practice. Makes testing and configuration easier. |
| **Blueprints per feature** | Keeps routes organized. Each blueprint has its own `routes.py` and `forms.py`. |
| **Services layer** | Business logic (availability checks, price calculations) lives in `services/`, NOT in route handlers. Routes should be thin. |
| **Models in separate files** | One file per model for clarity. All imported in `models/__init__.py`. |
| **Jinja2 template components** | Reusable partials prefixed with `_` (e.g., `_navbar.html`) included via `{% include %}`. |

---

## 5. Implementation Phases

> **For the implementer:** Work through these phases in order. Each phase builds on the previous one. Do NOT skip ahead. Each phase should result in working, testable functionality.

---

### Phase 1 — Project Scaffolding & Auth

**Goal:** A running Flask app with login/logout, a protected dashboard page, and the complete database schema migrated.

#### Tasks

- [ ] **1.1** Create the folder structure exactly as shown in Section 4.
- [ ] **1.2** Create `config.py` with a `Config` class that reads `SECRET_KEY` and `DATABASE_URL` from environment variables using `python-dotenv`. Set `SQLALCHEMY_TRACK_MODIFICATIONS = False`.
- [ ] **1.3** Create `app/extensions.py` — instantiate `SQLAlchemy`, `Migrate`, and `LoginManager` here (without binding to an app yet).
- [ ] **1.4** Create `app/__init__.py` with a `create_app()` factory function that:
  - Loads config
  - Initializes all extensions with `ext.init_app(app)`
  - Registers all blueprints
  - Sets `login_manager.login_view = 'auth.login'`
- [ ] **1.5** Create `run.py`:
  ```python
  from app import create_app
  app = create_app()
  if __name__ == '__main__':
      app.run(debug=True)
  ```
- [ ] **1.6** Create ALL model files (User, Product, Customer, Order, OrderItem) as defined in Section 3. Even though later phases implement the features, the **schema must exist now** so migrations work cleanly.
- [ ] **1.7** The `User` model must implement Flask-Login's `UserMixin` and include methods:
  - `set_password(password)` — uses `werkzeug.security.generate_password_hash`
  - `check_password(password)` — uses `werkzeug.security.check_password_hash`
- [ ] **1.8** Run initial migration:
  ```bash
  flask db init
  flask db migrate -m "initial schema"
  flask db upgrade
  ```
- [ ] **1.9** Create the **auth blueprint** with routes:
  - `GET /login` — render login form
  - `POST /login` — authenticate user, create session, redirect to dashboard
  - `GET /register` — render registration form (admin creates first account)
  - `POST /register` — create user, redirect to login
  - `GET /logout` — log out and redirect to login
- [ ] **1.10** Create `LoginForm` and `RegisterForm` using Flask-WTF with proper validators (DataRequired, Email, EqualTo for password confirmation).
- [ ] **1.11** Create `base.html` master template with:
  - TailwindCSS output.css linked
  - A sidebar navigation (links to Dashboard, Products, Customers, Orders)
  - A top navbar with logged-in user info and logout button
  - A `{% block content %}` for page content
  - Flash message display component
- [ ] **1.12** Create the **dashboard blueprint** with a single route:
  - `GET /` — protected by `@login_required`, renders a placeholder dashboard page that says "Welcome, {{ current_user.username }}".
- [ ] **1.13** Setup TailwindCSS build process and verify the compiled CSS works in the browser.

#### Acceptance Criteria
- [ ] `flask run` starts the app without errors.
- [ ] Visiting `/` while logged out redirects to `/login`.
- [ ] A user can register, login, see the dashboard, and logout.
- [ ] The sidebar navigation is visible and styled with TailwindCSS.
- [ ] All database tables exist in MySQL.

---

### Phase 2 — Product & Inventory Management

**Goal:** Full CRUD for products. Admin can add, view, edit, and soft-delete products. Product images can be uploaded.

#### Tasks

- [ ] **2.1** Create the **products blueprint** with routes:
  - `GET /products` — list all active products in a table/grid with columns: image thumbnail, name, category, daily rate, total stock, actions (edit/delete).
  - `GET /products/create` — render product form (empty).
  - `POST /products/create` — validate form, save product, redirect to product list.
  - `GET /products/<id>` — product detail page showing all info.
  - `GET /products/<id>/edit` — render product form (pre-filled).
  - `POST /products/<id>/edit` — validate, update product, redirect.
  - `POST /products/<id>/delete` — soft-delete (set `is_active = False`), redirect to list.
- [ ] **2.2** Create `ProductForm` (Flask-WTF) with fields: name, description, category, daily_rate, total_stock, image (FileField).
- [ ] **2.3** Implement image upload:
  - Save uploaded files to `app/static/uploads/` with a UUID filename to prevent collisions.
  - Store the relative path in `product.image_url`.
  - Validate file extension (allow: jpg, jpeg, png, webp only).
  - Set a max file size of 5MB in Flask config (`MAX_CONTENT_LENGTH`).
- [ ] **2.4** Auto-generate the `slug` field from the product name using `slugify` (install `python-slugify`). Ensure uniqueness by appending a number if a duplicate exists.
- [ ] **2.5** Add **search and filter** to the product list:
  - A search input that filters by product name (SQL `LIKE`).
  - A category dropdown filter.
  - Pagination (10 items per page) using Flask-SQLAlchemy's `paginate()`.
- [ ] **2.6** Create the product list template (`products/list.html`) as a responsive table. On mobile, switch to a card layout using Tailwind breakpoints.
- [ ] **2.7** Create the product detail template (`products/detail.html`) showing all product info, the image, and an "Edit" button.
- [ ] **2.8** Create the shared form template (`products/form.html`) that handles both create and edit modes based on whether a product object is passed.

#### Acceptance Criteria
- [ ] Admin can create a product with an image, view it in the list, click into it, edit it, and soft-delete it.
- [ ] Searching by name and filtering by category works.
- [ ] Pagination works when there are more than 10 products.
- [ ] Image uploads are saved to disk and display correctly.

---

### Phase 3 — Customer Management

**Goal:** Full CRUD for customers. Admin can manage customers and see their future order history (orders come in Phase 4).

#### Tasks

- [ ] **3.1** Create the **customers blueprint** with routes:
  - `GET /customers` — list all customers in a table: name, email, phone, number of orders, actions.
  - `GET /customers/create` — render customer form.
  - `POST /customers/create` — validate, save, redirect.
  - `GET /customers/<id>` — customer detail page with contact info and order history (empty for now, will populate in Phase 4).
  - `GET /customers/<id>/edit` — render edit form.
  - `POST /customers/<id>/edit` — validate, update, redirect.
  - `POST /customers/<id>/delete` — hard-delete customer (only if they have zero orders; else show error flash message).
- [ ] **3.2** Create `CustomerForm` (Flask-WTF) with fields: first_name, last_name, email, phone, address, notes.
- [ ] **3.3** Add search to the customer list (search by name or email).
- [ ] **3.4** Add pagination (10 per page).
- [ ] **3.5** On the customer detail page, include a section titled "Order History" with placeholder text: *"No orders yet."* (This will be populated in Phase 4.)

#### Acceptance Criteria
- [ ] Admin can create, view, edit, and delete customers.
- [ ] Deleting a customer with orders shows an error message.
- [ ] Search by name/email works.

---

### Phase 4 — Orders & Booking Engine

**Goal:** Admin can create orders (bookings) that tie customers to products for a date range. Order totals are auto-calculated.

#### Tasks

- [ ] **4.1** Create the **orders blueprint** with routes:
  - `GET /orders` — list all orders in a table: order number, customer name, status, rental dates, total, actions.
  - `GET /orders/create` — render order creation form.
  - `POST /orders/create` — validate, check availability, create order + order items, calculate totals, redirect.
  - `GET /orders/<id>` — order detail page showing all info, line items, and status.
  - `GET /orders/<id>/edit` — edit order (only if status is `draft` or `confirmed`).
  - `POST /orders/<id>/edit` — validate, update, recalculate totals.
  - `POST /orders/<id>/status` — change order status (the request body sends the new status).
  - `POST /orders/<id>/cancel` — set status to `cancelled`.
- [ ] **4.2** Create `OrderForm` with fields:
  - `customer_id` — SelectField, populated from the customers table.
  - `rental_start` — DateField.
  - `rental_end` — DateField (must be ≥ rental_start).
  - `discount` — DecimalField (optional, default 0).
  - `tax_rate` — DecimalField (optional, default 0).
  - `notes` — TextAreaField.
- [ ] **4.3** Create `OrderItemForm` (inline/nested):
  - `product_id` — SelectField, populated from active products.
  - `quantity` — IntegerField (min 1).
  - Handle **multiple order items** per order. Use JavaScript to dynamically add/remove product rows on the form.
- [ ] **4.4** Create `app/services/order_service.py` with functions:
  - `calculate_rental_days(start_date, end_date)` → returns integer number of days (minimum 1).
  - `calculate_line_total(quantity, daily_rate, num_days)` → returns Decimal.
  - `calculate_order_totals(order)` → sets `subtotal`, `total` on the order based on its items, discount, and tax_rate.
  - `generate_order_number()` → returns a unique string like `ORD-20260813-001` (date + sequential counter for that date).
- [ ] **4.5** When creating/editing an order, snapshot the product's `daily_rate` into `order_items.daily_rate` so that future price changes don't affect past orders.
- [ ] **4.6** Implement the **order status workflow**:
  ```
  draft → confirmed → picked_up → returned
                 ↘ cancelled
  draft → cancelled
  ```
  - Validate transitions: e.g., cannot go from `returned` back to `picked_up`.
  - Display the current status as a colored badge on the order detail page.
- [ ] **4.7** On the **customer detail page** (from Phase 3), now show real order history — a table of all orders for that customer, sorted by most recent first.
- [ ] **4.8** Add filters to the order list page:
  - Filter by status (dropdown).
  - Filter by date range (rental_start between two dates).
  - Search by order number or customer name.
  - Pagination (10 per page).
- [ ] **4.9** Write JavaScript (`app/static/js/app.js`) to handle:
  - Dynamic add/remove of order item rows in the order form.
  - Date validation (end date ≥ start date) on the client side.

#### Acceptance Criteria
- [ ] Admin can create an order with multiple products, selecting a customer and date range.
- [ ] Order totals (subtotal, tax, total) are calculated correctly.
- [ ] Status transitions work and invalid transitions are rejected.
- [ ] Customer detail page shows that customer's orders.
- [ ] Order list filters and search work.

---

### Phase 5 — Availability Engine

**Goal:** The system prevents overbooking. When creating or editing an order, the system checks that enough stock is available for the requested products and dates.

#### Tasks

- [ ] **5.1** Create `app/services/availability.py` with functions:
  - `get_booked_quantity(product_id, start_date, end_date, exclude_order_id=None)`:
    - Query all **non-cancelled** order_items for this product where the order's rental period overlaps with `[start_date, end_date]`.
    - Sum their quantities.
    - `exclude_order_id` is used when editing an existing order (don't count the order being edited).
    - **Date overlap logic:** Two ranges `[A_start, A_end]` and `[B_start, B_end]` overlap if `A_start <= B_end AND A_end >= B_start`.
  - `get_available_quantity(product_id, start_date, end_date, exclude_order_id=None)`:
    - Returns `product.total_stock - get_booked_quantity(...)`.
  - `check_availability(items, start_date, end_date, exclude_order_id=None)`:
    - `items` is a list of `{product_id, quantity}`.
    - Returns a list of error messages for any product where requested quantity exceeds available quantity.
    - Returns an empty list if everything is available.
- [ ] **5.2** Integrate availability checks into the order creation and edit routes:
  - Before saving, call `check_availability()`.
  - If errors are returned, flash them and re-render the form (do NOT save the order).
- [ ] **5.3** On the product detail page, add an **availability calendar** (simple version):
  - Show the next 30 days as a list/grid.
  - For each day, show how many units are available.
  - Use color coding: green (all available), yellow (some booked), red (fully booked).
- [ ] **5.4** When a product is selected in the order form, show available quantity for the selected date range via an AJAX endpoint:
  - `GET /api/availability?product_id=X&start=YYYY-MM-DD&end=YYYY-MM-DD` → returns JSON `{ "available": N }`.
  - Use JavaScript to fetch and display this when the user changes the product or dates.

#### Acceptance Criteria
- [ ] Creating an order for 5 units when only 3 are available shows an error and does NOT save.
- [ ] Editing an order correctly excludes itself from the availability count.
- [ ] The product detail page shows a 30-day availability view.
- [ ] The AJAX availability check works in the order form.

---

### Phase 6 — Invoicing & Payments

**Goal:** Generate a printable invoice for each order. Track payment status manually.

#### Tasks

- [ ] **6.1** Add payment-related columns to the `orders` table (create a new migration):
  - `payment_status` — VARCHAR(20), DEFAULT `'unpaid'`. Values: `unpaid`, `partially_paid`, `paid`.
  - `amount_paid` — DECIMAL(10,2), DEFAULT 0.
- [ ] **6.2** Create the **invoices blueprint** with routes:
  - `GET /orders/<id>/invoice` — render a clean, printable invoice page (no sidebar/navbar, just the invoice).
- [ ] **6.3** The invoice template (`invoices/detail.html`) must include:
  - Business name / address (hardcoded or from settings — see Phase 8).
  - Customer name and contact.
  - Order number, date created, rental start/end.
  - Line items table: product name, quantity, daily rate, days, line total.
  - Subtotal, discount, tax, **grand total**.
  - Payment status.
  - A "Print" button that calls `window.print()`.
- [ ] **6.4** Add CSS `@media print` styles to hide the print button and any non-invoice elements when printing.
- [ ] **6.5** Add a **Record Payment** form on the order detail page:
  - An input for the amount being paid.
  - A submit button that updates `amount_paid` and auto-sets `payment_status`:
    - If `amount_paid >= total` → `paid`
    - If `amount_paid > 0 but < total` → `partially_paid`
    - If `amount_paid == 0` → `unpaid`
- [ ] **6.6** Display payment status as a colored badge on the order detail and order list pages.

#### Acceptance Criteria
- [ ] Clicking "View Invoice" on an order shows a clean, printable invoice.
- [ ] Printing the page produces a clean PDF/print output.
- [ ] Recording a payment correctly updates the payment status.
- [ ] Payment status badges appear on order list and detail pages.

---

### Phase 7 — Dashboard & Reporting

**Goal:** The dashboard shows useful business metrics and charts.

#### Tasks

- [ ] **7.1** Update the **dashboard route** to query and pass the following data to the template:
  - **Summary Cards:**
    - Total active orders (status = `confirmed` or `picked_up`)
    - Total revenue this month (sum of `total` for orders with `rental_start` in current month, excluding cancelled)
    - Total customers
    - Total products
  - **Recent Orders:** Last 5 orders (order number, customer, status, total).
  - **Orders by Status:** Count of orders grouped by status.
  - **Top 5 Products:** Products with the most order_items (by quantity) in the last 30 days.
- [ ] **7.2** Design the dashboard template with:
  - 4 summary cards at the top (icon, label, value) — use Tailwind grid.
  - A "Recent Orders" table below.
  - Two side-by-side sections: "Orders by Status" (simple bar or list) and "Top Products" (simple list with bar indicators).
- [ ] **7.3** (Optional) Add a simple chart using Chart.js (CDN) for "Revenue over last 6 months" — a bar chart.
  - Create a route `GET /api/dashboard/revenue` that returns monthly revenue data as JSON.
  - Render the chart in JavaScript on the dashboard page.

#### Acceptance Criteria
- [ ] Dashboard loads with real data from the database.
- [ ] Summary cards display correct numbers.
- [ ] Recent orders table links to order detail pages.
- [ ] (If Chart.js is used) The revenue chart renders correctly.

---

### Phase 8 — Polish, Settings & Deployment

**Goal:** Final polish, a settings page, and production readiness.

#### Tasks

- [ ] **8.1** Create a **settings page** (`GET /settings`) where the admin can configure:
  - Business name
  - Business address
  - Default tax rate
  - Store these in a `settings` table (key-value pairs) or a single-row `business_settings` table.
  - These values are used in invoices and order calculations.
- [ ] **8.2** Add **flash messages** throughout the app for all user actions:
  - Success: "Product created successfully."
  - Error: "Could not delete customer — they have existing orders."
  - Warning: "Only 2 units available for [Product Name]."
  - Use Tailwind-styled alert banners (green for success, red for error, yellow for warning).
- [ ] **8.3** Add a **confirmation modal** (`_confirm_modal.html`) for all delete actions. Use JavaScript to intercept the delete button click, show the modal, and only submit the form on confirmation.
- [ ] **8.4** Responsive design check:
  - Test all pages at mobile (375px), tablet (768px), and desktop (1280px) widths.
  - The sidebar should collapse into a hamburger menu on mobile.
  - Tables should be horizontally scrollable on small screens.
- [ ] **8.5** Add proper **error pages**:
  - `404.html` — "Page not found" with a link back to the dashboard.
  - `500.html` — "Something went wrong" with a generic message.
  - Register these with `@app.errorhandler(404)` and `@app.errorhandler(500)`.
- [ ] **8.6** Add a `seed.py` script at the project root that:
  - Creates a default admin user (username: `admin`, password: `admin123`).
  - Creates 10 sample products with varied categories and stock levels.
  - Creates 5 sample customers.
  - Creates 3 sample orders with order items.
  - Run with `python seed.py`.
- [ ] **8.7** Create a `.gitignore` that ignores:
  ```
  venv/
  __pycache__/
  .env
  node_modules/
  app/static/css/output.css
  app/static/uploads/
  *.pyc
  instance/
  migrations/
  ```
- [ ] **8.8** Write a `README.md` with:
  - Project description.
  - Setup instructions (Python, Node, MySQL, migrations).
  - How to run the development server.
  - How to seed the database.
  - Screenshots (add later).

#### Acceptance Criteria
- [ ] Settings page works and invoice uses saved business info.
- [ ] All delete actions show a confirmation modal.
- [ ] The app is responsive on mobile, tablet, and desktop.
- [ ] 404 and 500 error pages render correctly.
- [ ] `python seed.py` populates the database with sample data.
- [ ] `README.md` is complete and accurate.

---

## 6. UI/UX Guidelines

> **For the implementer:** Follow these guidelines for all templates.

### Layout

- Use a **sidebar + main content** layout.
- Sidebar: fixed on the left (width: 250px on desktop), collapsible on mobile.
- Sidebar items: Dashboard, Products, Customers, Orders, Settings.
- Each sidebar item should have an icon (use [Heroicons](https://heroicons.com/) — inline SVG or copy from the site).
- Main content area: padded, max-width container.

### Color Palette (Tailwind Classes)

| Purpose          | Class                        | Use For                     |
|:-----------------|:-----------------------------|:----------------------------|
| Primary          | `bg-indigo-600`, `text-indigo-600` | Buttons, active sidebar item, links |
| Primary Hover    | `hover:bg-indigo-700`        | Button hover states         |
| Success          | `bg-green-500`               | Success badges, flash messages |
| Warning          | `bg-yellow-500`              | Warning badges, low stock   |
| Danger           | `bg-red-500`                 | Delete buttons, error states |
| Sidebar BG       | `bg-gray-900`                | Sidebar background          |
| Sidebar Text     | `text-gray-300`              | Sidebar link text           |
| Page BG          | `bg-gray-50`                 | Main content background     |
| Card BG          | `bg-white`                   | Content cards, tables       |

### Component Patterns

- **Tables:** Use `<table>` with Tailwind classes. Alternate row colors with `even:bg-gray-50`. Add `hover:bg-gray-100` to rows.
- **Cards:** `bg-white rounded-lg shadow-sm p-6`.
- **Buttons:**
  - Primary: `bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700`
  - Danger: `bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700`
  - Secondary: `bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50`
- **Form Inputs:** `w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500`
- **Badges (status):**
  - draft → `bg-gray-100 text-gray-700`
  - confirmed → `bg-blue-100 text-blue-700`
  - picked_up → `bg-yellow-100 text-yellow-700`
  - returned → `bg-green-100 text-green-700`
  - cancelled → `bg-red-100 text-red-700`

### Typography

- Headings: `text-2xl font-bold text-gray-900` for page titles, `text-lg font-semibold` for section headers.
- Body text: `text-sm text-gray-600` or `text-base text-gray-700`.
- Use Inter or the system font stack (Tailwind's default).

---

## 7. API Route Map

> **For the implementer:** This is the complete list of routes. Use this as a checklist.

### Auth (`/auth`)
| Method | URL                 | Description          | Auth Required |
|:-------|:--------------------|:---------------------|:--------------|
| GET    | `/auth/login`       | Login page           | No            |
| POST   | `/auth/login`       | Process login        | No            |
| GET    | `/auth/register`    | Register page        | No            |
| POST   | `/auth/register`    | Process registration | No            |
| GET    | `/auth/logout`      | Log out              | Yes           |

### Dashboard (`/`)
| Method | URL | Description       | Auth Required |
|:-------|:----|:------------------|:--------------|
| GET    | `/` | Dashboard home    | Yes           |

### Products (`/products`)
| Method | URL                      | Description             | Auth Required |
|:-------|:-------------------------|:------------------------|:--------------|
| GET    | `/products`              | List products           | Yes           |
| GET    | `/products/create`       | Create form             | Yes           |
| POST   | `/products/create`       | Save new product        | Yes           |
| GET    | `/products/<id>`         | Product detail          | Yes           |
| GET    | `/products/<id>/edit`    | Edit form               | Yes           |
| POST   | `/products/<id>/edit`    | Update product          | Yes           |
| POST   | `/products/<id>/delete`  | Soft-delete product     | Yes           |

### Customers (`/customers`)
| Method | URL                       | Description             | Auth Required |
|:-------|:--------------------------|:------------------------|:--------------|
| GET    | `/customers`              | List customers          | Yes           |
| GET    | `/customers/create`       | Create form             | Yes           |
| POST   | `/customers/create`       | Save new customer       | Yes           |
| GET    | `/customers/<id>`         | Customer detail         | Yes           |
| GET    | `/customers/<id>/edit`    | Edit form               | Yes           |
| POST   | `/customers/<id>/edit`    | Update customer         | Yes           |
| POST   | `/customers/<id>/delete`  | Delete customer         | Yes           |

### Orders (`/orders`)
| Method | URL                       | Description             | Auth Required |
|:-------|:--------------------------|:------------------------|:--------------|
| GET    | `/orders`                 | List orders             | Yes           |
| GET    | `/orders/create`          | Create form             | Yes           |
| POST   | `/orders/create`          | Save new order          | Yes           |
| GET    | `/orders/<id>`            | Order detail            | Yes           |
| GET    | `/orders/<id>/edit`       | Edit form               | Yes           |
| POST   | `/orders/<id>/edit`       | Update order            | Yes           |
| POST   | `/orders/<id>/status`     | Change status           | Yes           |
| POST   | `/orders/<id>/cancel`     | Cancel order            | Yes           |
| GET    | `/orders/<id>/invoice`    | View invoice            | Yes           |
| POST   | `/orders/<id>/payment`    | Record payment          | Yes           |

### API (JSON Endpoints)
| Method | URL                                | Description              | Auth Required |
|:-------|:-----------------------------------|:-------------------------|:--------------|
| GET    | `/api/availability`                | Check product availability| Yes          |
| GET    | `/api/dashboard/revenue`           | Monthly revenue data     | Yes           |

### Settings (`/settings`)
| Method | URL          | Description         | Auth Required |
|:-------|:-------------|:--------------------|:--------------|
| GET    | `/settings`  | Settings page       | Yes           |
| POST   | `/settings`  | Save settings       | Yes           |

---

## 8. Testing Strategy

> **For the implementer:** At minimum, write tests for the services layer. Use `pytest`.

### Setup
```bash
pip install pytest
```

### What to Test

| Area | What to Test | Priority |
|:-----|:-------------|:---------|
| `availability.py` | `get_booked_quantity` returns correct count for overlapping, non-overlapping, and cancelled orders | **High** |
| `availability.py` | `get_available_quantity` returns `total_stock - booked` | **High** |
| `availability.py` | `check_availability` returns errors when over-capacity, empty list when OK | **High** |
| `order_service.py` | `calculate_rental_days` returns correct day count (inclusive) | **High** |
| `order_service.py` | `calculate_line_total` computes correctly | **High** |
| `order_service.py` | `calculate_order_totals` handles discount and tax | **High** |
| `order_service.py` | `generate_order_number` produces unique, correctly formatted strings | Medium |
| Auth routes | Login with valid/invalid credentials | Medium |
| Product CRUD | Creating and editing products updates the database | Medium |
| Order status | Valid transitions succeed, invalid ones return errors | Medium |

### Test File Location
Place test files in a `tests/` directory at the project root:
```
tests/
├── conftest.py           # Fixtures: test app, test client, test db
├── test_availability.py
├── test_order_service.py
└── test_routes.py        # Optional: route-level integration tests
```

### conftest.py Pattern
```python
import pytest
from app import create_app
from app.extensions import db as _db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
```

---

## 9. Conventions & Rules

> **For the implementer:** Follow these rules strictly across the entire codebase.

### Python
1. **All routes must be protected** with `@login_required` except login and register.
2. **Never write raw SQL.** Always use SQLAlchemy ORM queries.
3. **Never put business logic in routes.** Routes handle HTTP (parse request, call service, return response). Logic goes in `services/`.
4. **Use flash messages** for user feedback after every create, update, delete, and error action.
5. **Validate all forms server-side** using Flask-WTF validators, even if client-side validation exists.
6. **Use `db.session.commit()` carefully.** Wrap in try/except and `db.session.rollback()` on failure.
7. **Follow PEP 8.** Use 4-space indentation, snake_case for variables/functions, PascalCase for classes.

### Templates (Jinja2)
1. **Every page extends `base.html`.**
2. **Use `{% include %}` for reusable components** (prefixed with `_`).
3. **Never use inline styles.** Use Tailwind utility classes.
4. **All forms must include `{{ form.hidden_tag() }}`** for CSRF protection.

### Database
1. **All schema changes go through Flask-Migrate.** Run `flask db migrate` and `flask db upgrade`.
2. **Never modify the database manually** (no raw `ALTER TABLE` commands).
3. **Use soft-delete** for products (set `is_active = False`). Hard-delete for customers only if they have no orders.

### Git
1. Commit after completing each phase.
2. Use descriptive commit messages: `feat: add product CRUD with image upload`.
3. Never commit `.env`, `node_modules/`, `venv/`, or compiled CSS.
