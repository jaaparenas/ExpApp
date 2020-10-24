from flask import Blueprint

datos = Blueprint('datos', __name__, url_prefix='/1.0/datos')

from . import routes, models