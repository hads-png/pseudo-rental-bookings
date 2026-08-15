from flask import Blueprint

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')

from app.blueprints.calendar import routes
