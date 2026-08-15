"""
Customer service layer — business logic for customer CRUD operations.
Decoupled from route handlers (Section 9, Convention #3).
"""
from app.extensions import db
from app.models.customer import Customer


def create_customer(form_data: dict) -> Customer:
    """Create a new customer record in the database.

    Args:
        form_data: Validated form data dictionary.

    Returns:
        The newly created Customer instance.
    """
    customer = Customer(
        first_name=form_data['first_name'].strip(),
        last_name=form_data['last_name'].strip(),
        email=form_data['email'].strip().lower(),
        phone=form_data.get('phone', '').strip() if form_data.get('phone') else None,
        address=form_data.get('address', '').strip() if form_data.get('address') else None,
        notes=form_data.get('notes', '').strip() if form_data.get('notes') else None
    )

    try:
        db.session.add(customer)
        db.session.commit()
        return customer
    except Exception:
        db.session.rollback()
        raise


def update_customer(customer: Customer, form_data: dict) -> Customer:
    """Update an existing customer record.

    Args:
        customer: The Customer instance to update.
        form_data: Validated form data dictionary.

    Returns:
        The updated Customer instance.
    """
    customer.first_name = form_data['first_name'].strip()
    customer.last_name = form_data['last_name'].strip()
    customer.email = form_data['email'].strip().lower()
    customer.phone = form_data.get('phone', '').strip() if form_data.get('phone') else None
    customer.address = form_data.get('address', '').strip() if form_data.get('address') else None
    customer.notes = form_data.get('notes', '').strip() if form_data.get('notes') else None

    try:
        db.session.commit()
        return customer
    except Exception:
        db.session.rollback()
        raise


def delete_customer(customer: Customer) -> tuple[bool, str]:
    """Hard-delete a customer only if they have zero orders.

    As per Section 8.2 and Section 9 conventions:
    If a customer has orders, deletion is rejected with the exact error message:
    "Could not delete customer — they have existing orders."

    Args:
        customer: The Customer instance to delete.

    Returns:
        A tuple of (success_boolean, message_string).
    """
    # Check if customer has associated orders
    if customer.orders.count() > 0:
        return False, "Could not delete customer — they have existing orders."

    try:
        customer_name = customer.full_name
        db.session.delete(customer)
        db.session.commit()
        return True, f"Customer '{customer_name}' was deleted."
    except Exception:
        db.session.rollback()
        return False, "An error occurred while deleting the customer. Please try again."
