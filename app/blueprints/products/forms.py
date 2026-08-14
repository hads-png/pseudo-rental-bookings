from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[
        DataRequired(message='Product name is required.'),
        Length(max=150, message='Product name must be under 150 characters.')
    ])
    category = StringField('Category', validators=[
        Optional(),
        Length(max=100, message='Category must be under 100 characters.')
    ])
    daily_rate = DecimalField('Daily Rate ($)', validators=[
        DataRequired(message='Daily rate is required.'),
        NumberRange(min=0.01, message='Daily rate must be at least $0.01.')
    ], places=2)
    total_stock = IntegerField('Total Stock (Units)', validators=[
        DataRequired(message='Total stock is required.'),
        NumberRange(min=0, message='Stock cannot be negative.')
    ])
    description = TextAreaField('Description', validators=[
        Optional()
    ])
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (JPG, PNG, WEBP).')
    ])
    submit = SubmitField('Save Product')
