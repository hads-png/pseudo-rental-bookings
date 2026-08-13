from flask import Blueprint

invoices_bp = Blueprint('invoices', __name__, url_prefix='/invoices')

from app.blueprints.invoices import routes  # noqa: E402, F401
