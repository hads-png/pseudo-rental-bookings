# Phase 4 — Orders & Booking Engine

**Goal:** Admin can create, view, edit, filter, and transition rental orders (bookings) tying customers to multiple products for specified date ranges with automatic financial calculations.

## Tasks

- [x] **4.1** Create `app/services/order_service.py` for calculation engine, order number generation (`ORD-YYYYMMDD-XXX`), snapshotting product daily rates into `order_item.daily_rate`, line item subtotal calculations, and status transitions.
- [x] **4.2** Create `app/blueprints/orders/forms.py` with `OrderForm` and `OrderItemForm` (using Flask-WTF `FieldList` and `FormField`).
- [x] **4.3** Implement Order routes in `app/blueprints/orders/routes.py`:
  - `GET /orders` — List orders with status, date range, and keyword search/filters with pagination.
  - `GET /orders/create` & `POST /orders/create` — Create order.
  - `GET /orders/<id>` — Detail invoice view with financial breakdown and status transition action controls.
  - `GET /orders/<id>/edit` & `POST /orders/<id>/edit` — Edit order (draft & confirmed orders only).
  - `POST /orders/<id>/status` — Trigger status state transitions.
  - `POST /orders/<id>/cancel` — Cancel order.
- [x] **4.4** Add client-side dynamic item repeater and date range validation in `app/static/js/app.js`.
- [x] **4.5** Create templates: `orders/list.html`, `orders/form.html`, `orders/detail.html`.
- [x] **4.6** Update Customer detail page order history section to show actual past orders.
- [x] **4.7** Write unit tests in `tests/test_order_service.py` and integration tests in `tests/test_orders.py`.

## Acceptance Criteria
- [x] Order numbers are auto-generated in format `ORD-YYYYMMDD-XXX`.
- [x] Inclusive rental days calculation (`(end - start).days + 1`).
- [x] Product daily rates snapshotted at time of creation/edit.
- [x] Financial totals (subtotal, discount, tax, total) computed using precise Decimal arithmetic.
- [x] Status transitions enforced (`draft` -> `confirmed` -> `picked_up` -> `returned`, `cancelled`).
- [x] Edits restricted to `draft` and `confirmed` orders.
