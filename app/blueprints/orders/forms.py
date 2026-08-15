from decimal import Decimal
from wtforms import Form, SelectField, IntegerField, DateField, DecimalField, TextAreaField, SubmitField, FieldList, FormField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError


class OrderItemForm(Form):
    product_id = SelectField('Product', coerce=int, validators=[DataRequired(message='Please select a product.')])
    quantity = IntegerField('Quantity', default=1, validators=[
        DataRequired(message='Quantity is required.'),
        NumberRange(min=1, message='Quantity must be at least 1.')
    ])


class OrderForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired(message='Please select a customer.')])
    rental_start = DateField('Rental Start Date', format='%Y-%m-%d', validators=[DataRequired(message='Start date is required.')])
    rental_end = DateField('Rental End Date', format='%Y-%m-%d', validators=[DataRequired(message='End date is required.')])
    discount = DecimalField('Discount ($)', default=Decimal('0.00'), places=2, validators=[
        Optional(),
        NumberRange(min=0, message='Discount cannot be negative.')
    ])
    tax_rate = DecimalField('Tax Rate', default=Decimal('0.0000'), places=4, validators=[
        Optional(),
        NumberRange(min=0, max=1, message='Tax rate must be between 0 and 1 (e.g., 0.10 for 10%).')
    ])
    notes = TextAreaField('Internal Notes', validators=[Optional()])
    items = FieldList(FormField(OrderItemForm), min_entries=1)
    submit = SubmitField('Save Order')

    def validate_rental_end(self, field):
        if self.rental_start.data and field.data:
            if field.data < self.rental_start.data:
                raise ValidationError('Rental end date cannot be earlier than start date.')
