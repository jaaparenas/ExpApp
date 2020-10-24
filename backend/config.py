import os
basedir = os.path.abspath(os.path.dirname(__file__))
#postgres_local_base = 'postgresql://postgres:@localhost/'
#database_name = 'flask_jwt_auth'


class Config(object):
    # APP MODE
    DEBUG = True

    # Cors Control
    CORS_HEADERS = 'cache-control'

    # Top secret of website
    SECRET_KEY = os.environ.get('SECRET_KEY') or '***REMOVED***'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or '***REMOVED***'

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload Files
    UPLOAD_FOLDER =  os.path.join(basedir, 'storage/uploads')
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xls', 'xlsx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Mail Configuration
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '***REMOVED***'
    MAIL_PASSWORD = '***REMOVED***'

    # ADMINS
    ADMINS = ['***REMOVED***']

    BCRYPT_LOG_ROUNDS = 13