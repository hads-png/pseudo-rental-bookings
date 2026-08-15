from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.settings import Settings
from app.blueprints.settings import settings_bp
from app.blueprints.settings.forms import SettingsForm


@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    settings = Settings.get_settings()
    form = SettingsForm(obj=settings)

    if form.validate_on_submit():
        settings.business_name = form.business_name.data
        settings.business_address = form.business_address.data
        settings.default_tax_rate = form.default_tax_rate.data
        db.session.commit()
        flash('Settings updated successfully.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/index.html', form=form, settings=settings)
