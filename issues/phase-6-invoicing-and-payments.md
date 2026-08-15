# Issue 6: Phase 6 — Invoicing & Payments

**Status:** Completed  
**Assignee:** AI Developer  
**Phase:** 6 of 8  

---

### Description
Generate printable invoices for orders and provide manual payment tracking functionality.

---

### Objectives & Tasks
- [x] **6.1 Verified Data Schema:** `payment_status` and `amount_paid` columns are present on `Order`.
- [x] **6.2 Printable Invoice Page:** Created standalone print-optimized template `app/templates/invoices/detail.html`.
- [x] **6.3 Invoice Routes:** Created routes `GET /orders/<id>/invoice` and `GET /invoices/<id>` to display invoice data.
- [x] **6.4 CSS Print Styles:** Added `window.print()` trigger and `@media print` + Tailwind `no-print` hiding for header actions.
- [x] **6.5 Record Payment:** Created `POST /orders/<id>/payment` handling manual payments and transitioning status (`unpaid` → `partially_paid` → `paid`).
- [x] **6.6 Status Badges:** Updated `orders/detail.html` and `orders/list.html` to show payment badges.
- [x] **6.7 Comprehensive Testing:** Added `tests/test_invoices.py` covering invoice rendering and payment transitions.

---

### Acceptance Criteria
- [x] Clicking "View Invoice" renders a clean printable page without sidebar/navbar.
- [x] `window.print()` works without displaying non-invoice controls on print.
- [x] Recording payments dynamically updates `amount_paid` and `payment_status`.
- [x] All unit and integration tests pass cleanly.
