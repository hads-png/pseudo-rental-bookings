# Phase 3 — Customer Management

**Goal:** Full CRUD for customers. Admin can manage customers and see their future order history (orders come in Phase 4).

## Tasks

- [x] **3.1** Create the **customers blueprint** with routes:
  - `GET /customers` — list all customers in a table: name, email, phone, number of orders, actions.
  - `GET /customers/create` — render customer form.
  - `POST /customers/create` — validate, save, redirect.
  - `GET /customers/<id>` — customer detail page with contact info and order history (empty for now, will populate in Phase 4).
  - `GET /customers/<id>/edit` — render edit form.
  - `POST /customers/<id>/edit` — validate, update, redirect.
  - `POST /customers/<id>/delete` — hard-delete customer (only if they have zero orders; else show error flash message).
- [x] **3.2** Create `CustomerForm` (Flask-WTF) with fields: first_name, last_name, email, phone, address, notes.
- [x] **3.3** Add search to the customer list (search by name or email).
- [x] **3.4** Add pagination (10 per page).
- [x] **3.5** On the customer detail page, include a section titled "Order History" with placeholder text: *"No orders yet."* (This will be populated in Phase 4.)

## Acceptance Criteria
- [x] Admin can create, view, edit, and delete customers.
- [x] Deleting a customer with orders shows an error message (`"Could not delete customer — they have existing orders."`).
- [x] Search by name/email works.
