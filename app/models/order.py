from datetime import datetime, timezone
from app.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, confirmed, picked_up, returned, cancelled
    rental_start = db.Column(db.DateTime, nullable=False)
    rental_end = db.Column(db.DateTime, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    discount = db.Column(db.Numeric(10, 2), default=0.00)
    tax_rate = db.Column(db.Numeric(5, 4), default=0.0000)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, partially_paid, paid
    amount_paid = db.Column(db.Numeric(10, 2), default=0.00)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    customer = db.relationship('Customer', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Order {self.order_number} ({self.status})>'
