import os
import secrets

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


def _env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return list(default or [])
    return [item.strip() for item in value.split(',') if item.strip()]


class Config(object):
    # APP MODE
    ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = _env_bool('FLASK_DEBUG', False)

    # CORS: lista de orígenes separada por comas. Vacío = sin CORS cruzado.
    CORS_ORIGINS = _env_list(
        'CORS_ORIGINS',
        ['http://localhost:3000', 'http://127.0.0.1:3000'] if DEBUG else []
    )

    # Secretos. Sin valores por defecto: se validan al crear la aplicación.
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload Files
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(basedir, 'storage/uploads')
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xls', 'xlsx'}
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = _env_bool('MAIL_USE_TLS', True)
    MAIL_USE_SSL = _env_bool('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # URLs used to build links (password recovery, etc.)
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5000')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

    # ADMINS
    ADMINS = _env_list('ADMINS')

    BCRYPT_LOG_ROUNDS = int(os.environ.get('BCRYPT_LOG_ROUNDS', 13))
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    ALLOW_REGISTRATION = _env_bool('ALLOW_REGISTRATION', False)

    # JWT / tokens
    JWT_ISSUER = os.environ.get('JWT_ISSUER', 'expapp')
    ACCESS_TOKEN_EXPIRES = int(os.environ.get('ACCESS_TOKEN_EXPIRES', 60 * 60 * 24))
    REFRESH_TOKEN_EXPIRES = int(os.environ.get('REFRESH_TOKEN_EXPIRES', 60 * 60 * 24 * 7))
    RESET_TOKEN_EXPIRES = int(os.environ.get('RESET_TOKEN_EXPIRES', 60 * 60))

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://')
    RATELIMIT_HEADERS_ENABLED = True
    RATELIMIT_ENABLED = _env_bool('RATELIMIT_ENABLED', True)

    # Upload limit per file (bytes)
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 8 * 1024 * 1024))

    @classmethod
    def validate(cls):
        """Falla rápido si faltan secretos obligatorios."""
        missing = [
            name for name in ('SECRET_KEY', 'JWT_SECRET_KEY')
            if not getattr(cls, name, None)
        ]
        if missing:
            raise RuntimeError(
                'Faltan variables de entorno obligatorias: {}. '
                'Copia backend/.env.example a backend/.env y genera valores seguros '
                '(python -c "import secrets; print(secrets.token_hex(32))").'.format(
                    ', '.join(missing)
                )
            )


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = secrets.token_hex(32)
    JWT_SECRET_KEY = secrets.token_hex(32)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CORS_ORIGINS = []
    BCRYPT_LOG_ROUNDS = 4
    RATELIMIT_ENABLED = False
    ALLOW_REGISTRATION = False
    MAIL_DEFAULT_SENDER = 'no-reply@example.com'
