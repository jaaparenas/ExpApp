from flask import Blueprint

core = Blueprint('core', __name__, url_prefix='/')

from . import routes, models