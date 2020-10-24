from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/1.0/user')

from . import routes, models, decorators