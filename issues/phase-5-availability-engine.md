# Phase 5 — Availability Engine

**Goal:** The system prevents overbooking. When creating or editing an order, the system checks that enough stock is available for the requested products and dates.

## Tasks

- [x] **5.1** Create `app/services/availability.py` with functions:
  - `get_booked_quantity(product_id, start_date, end_date, exclude_order_id=None)`
  - `get_available_quantity(product_id, start_date, end_date, exclude_order_id=None)`
  - `check_availability(items, start_date, end_date, exclude_order_id=None)`
- [x] **5.2** Integrate availability checks into order creation and edit routes in `app/blueprints/orders/routes.py`. Flash errors if requested items exceed available stock and block saving.
- [x] **5.3** Create `app/blueprints/api/routes.py` with endpoint `GET /api/availability` returning JSON `{available, booked, total_stock}`. Registered blueprint `api_bp` in `app/__init__.py`.
- [x] **5.4** Add dynamic real-time AJAX product availability badges in `app/static/js/app.js` and `app/templates/orders/form.html`.
- [x] **5.5** Add a 30-day color-coded availability calendar grid on `app/templates/products/detail.html`.
- [x] **5.6** Write unit & integration test suite in `tests/test_availability.py`.

## Acceptance Criteria
- [x] Creating an order exceeding available stock is blocked with clear error flash messages.
- [x] Editing an order correctly excludes itself from booked quantity.
- [x] Product detail page displays a 30-day availability calendar with color-coded badges.
- [x] Real-time AJAX availability check updates in the order form upon product or date selection.
- [x] 100% test pass rate across all 46 unit and integration test cases.
