from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, NumberRange


class SettingsForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired()])
    business_address = TextAreaField('Business Address')
    default_tax_rate = DecimalField(
        'Default Tax Rate (e.g. 0.10 for 10%)',
        validators=[DataRequired(), NumberRange(min=0, max=1)],
        places=4
    )
