from datetime import datetime, timezone
from app.extensions import db


class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(150), nullable=False, default='Pseudo Booqable Rentals')
    business_address = db.Column(db.Text, nullable=True, default='123 Rental St, Suite 100\nCityville, ST 12345')
    default_tax_rate = db.Column(db.Numeric(5, 4), nullable=False, default=0.1000)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls(
                business_name='Pseudo Booqable Rentals',
                business_address='123 Rental St, Suite 100\nCityville, ST 12345',
                default_tax_rate=0.1000
            )
            db.session.add(settings)
            db.session.commit()
        return settings

    def __repr__(self) -> str:
        return f'<Settings {self.business_name}>'
