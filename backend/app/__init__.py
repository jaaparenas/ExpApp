import logging

from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException

from config import Config

bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()
cors = CORS()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)


def _register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'no-referrer')
        response.headers.setdefault(
            'Permissions-Policy',
            'geolocation=(), microphone=(), camera=()'
        )
        response.headers.setdefault(
            'Content-Security-Policy',
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        if request.path.startswith('/1.0/user'):
            response.headers.setdefault('Cache-Control', 'no-store')
        if app.config.get('ENV') == 'production' and not app.debug:
            response.headers.setdefault(
                'Strict-Transport-Security',
                'max-age=31536000; includeSubDomains'
            )
        return response


def _register_error_handlers(app):
    messages = {
        400: ('_BAD_REQUEST', 'Solicitud inválida'),
        401: ('_UNAUTHORIZED', 'No autorizado'),
        403: ('_FORBIDDEN', 'Prohibido'),
        404: ('_NOT_FOUND', 'Recurso no encontrado'),
        405: ('_METHOD_NOT_ALLOWED', 'Método no permitido'),
        413: ('_PAYLOAD_TOO_LARGE', 'El archivo es demasiado grande'),
        429: ('_TOO_MANY_REQUESTS', 'Demasiadas solicitudes'),
        500: ('_INTERNAL_ERROR', 'Error interno del servidor'),
    }

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        msg, description = messages.get(
            error.code, ('_HTTP_ERROR', 'Error HTTP')
        )
        return jsonify({'msg': msg, 'error': description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception('Error no controlado: %s', error)
        return jsonify({'msg': '_INTERNAL_ERROR'}), 500


def ExpApp(config=Config):
    config.validate()

    app = Flask(__name__)
    app.config.from_object(config)
    app.config.setdefault('JSON_SORT_KEYS', False)

    if not app.debug:
        app.logger.setLevel(logging.INFO)

    bcrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    if app.config.get('CORS_ORIGINS'):
        cors.init_app(app, resources={r'/*': {'origins': app.config['CORS_ORIGINS']}})
    migrate.init_app(app, db)
    limiter.init_app(app)

    _register_security_headers(app)
    _register_error_handlers(app)

    from app.auth import auth
    app.register_blueprint(auth)

    from app.core import core
    app.register_blueprint(core)

    from app.datos import datos
    app.register_blueprint(datos)

    return app
