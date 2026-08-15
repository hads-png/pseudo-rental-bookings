from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
from app.extensions import db
from app.models.customer import Customer


class CustomerForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required.'),
        Length(max=80, message='First name must be under 80 characters.')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required.'),
        Length(max=80, message='Last name must be under 80 characters.')
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Email address is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120, message='Email address must be under 120 characters.')
    ])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=30, message='Phone number must be under 30 characters.')
    ])
    address = TextAreaField('Address', validators=[Optional()])
    notes = TextAreaField('Internal Notes', validators=[Optional()])
    submit = SubmitField('Save Customer')

    def __init__(self, *args, customer_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_id = customer_id

    def validate_email(self, field):
        if not field.data:
            return
        email_clean = field.data.strip().lower()
        query = Customer.query.filter(db.func.lower(Customer.email) == email_clean)
        if self.customer_id:
            query = query.filter(Customer.id != self.customer_id)
        if query.first() is not None:
            raise ValidationError('A customer with this email address already exists.')
