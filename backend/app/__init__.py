from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_cors import CORS

from config import Config

bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()
cors = CORS()
migrate = Migrate()

def ExpApp(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    bcrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    migrate = Migrate(app, db)

    from app.auth import auth
    app.register_blueprint(auth)

    from app.core import core
    app.register_blueprint(core)

    from app.datos import datos
    app.register_blueprint(datos)

    return app
