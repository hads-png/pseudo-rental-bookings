from datetime import datetime, timezone
from app.extensions import db


class PricingTier(db.Model):
    __tablename__ = 'pricing_tiers'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "1 Day", "1 Week", "Hourly"
    duration_hours = db.Column(db.Integer, nullable=False) # e.g. 24 for daily, 168 for weekly
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    product = db.relationship('Product', back_populates='pricing_tiers')

    def __repr__(self) -> str:
        return f'<PricingTier {self.name} ({self.duration_hours}h) for Product {self.product_id}>'
