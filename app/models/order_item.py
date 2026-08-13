from datetime import datetime, timezone
from app.extensions import db


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    daily_rate = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

    def __repr__(self) -> str:
        return f'<OrderItem {self.id} (Order: {self.order_id}, Product: {self.product_id}, Qty: {self.quantity})>'
