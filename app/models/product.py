from datetime import datetime, timezone
from app.extensions import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    daily_rate = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total_stock = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    order_items = db.relationship('OrderItem', back_populates='product', lazy='dynamic')
    pricing_tiers = db.relationship('PricingTier', back_populates='product', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'<Product {self.name} (Stock: {self.total_stock})>'
