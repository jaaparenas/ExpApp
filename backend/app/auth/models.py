import jwt
import datetime
from ..core.models import BaseModel
from app import ExpApp, db, bcrypt


RolesUsers = db.Table('roles_users',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Role(db.Model, BaseModel):
  """
  Módelo administrar los Grupos de usuarios
  """
  __tablename__ = 'roles'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(255), unique=True, nullable=False)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  is_staff = db.Column(db.Boolean, nullable=False, default=False)
  is_guest = db.Column(db.Boolean, nullable=False, default=False)
  is_active = db.Column(db.Boolean, nullable=False, default=True)
  role_user = db.relationship('User', secondary=RolesUsers, lazy='subquery', backref=db.backref('roles', lazy=True))

  def __init__(self, name, is_admin=False, is_staff=False, is_guest=False, is_active=True):
    self.name = name
    self.is_admin = is_admin
    self.is_staff = is_staff
    self.is_guest = is_guest
    self.is_active = is_active

class User(db.Model, BaseModel):
  """ Modulo básico de usaurio """
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  username = db.Column(db.String(255), unique=True, nullable=False)
  first_name = db.Column(db.String(255), nullable=True)
  last_name = db.Column(db.String(255), nullable=True)
  email = db.Column(db.String(255), unique=True, nullable=False)
  password = db.Column(db.String(255), nullable=False)
  reset_password = db.Column(db.String(255), nullable=True)
  registered_on = db.Column(db.DateTime, nullable=False)
  is_active = db.Column(db.Boolean, nullable=False, default=False)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  role_user = db.relationship('Role', secondary=RolesUsers, lazy='subquery', backref=db.backref('users', lazy=True))

  def __init__(self, username, email, password, is_active=False, is_admin=False):
    self.username = username
    self.email = email
    self.password = bcrypt.generate_password_hash(password).decode()
    self.registered_on = datetime.datetime.now()
    self.first_name = ""
    self.last_name = ""
    self.is_active = is_active
    self.is_admin = is_admin

  def encode_tokens(self):
    """
    Genera un token JWT de autenticación
    :param user: Usuario autenticado
    :return: Object
    """
    try:
      token_access = {
        "token_type": "access",
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
        'user_id': self.id
      }
      token_refresh = {
        "token_type": "refresh",
        'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=1),
        'iat': datetime.datetime.utcnow(),
        'user_id': self.id
      }
      return {
        "access": jwt.encode(token_access, ExpApp().config['JWT_SECRET_KEY'], algorithm='HS256').decode('UTF-8'),
        "refresh": jwt.encode(token_refresh, ExpApp().config['JWT_SECRET_KEY'], algorithm='HS256').decode('UTF-8')
      }
    except Exception as e:
      return e

  @staticmethod
  def check_token(token, token_type='access'):
    """
    Válida el token JWT
    :param token: El token
    :param token_type: Tipo de token
    :return: integer|string
    """
    try:
      is_blacklisted_token = BlacklistToken.check_blacklist(token, token_type)
      if is_blacklisted_token:
        return '_BANNED_TOKEN'
      else:
        return True
    except:
      return '_INVALID_TOKEN'

  @staticmethod
  def decode_token(token):
    """
    Decodifica un token JWT
    :param token: El token
    :return: string
    """
    return jwt.decode(token, ExpApp().config['JWT_SECRET_KEY'])

class BlacklistToken(db.Model):
  """
  Módelo para controlar la negra de tokens JWT
  """
  __tablename__ = 'blacklist_tokens'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  token_type = db.Column(db.String(10), nullable=False)
  token = db.Column(db.String(500), unique=True, nullable=False)
  blacklisted_on = db.Column(db.DateTime, nullable=False)

  def __init__(self, token, token_type='access'):
    self.token = token
    self.token_type = token_type
    self.blacklisted_on = datetime.datetime.now()

  @staticmethod
  def check_blacklist(token, token_type='access'):
    """
    Verifica que el Token no este en la lista negra
    :param token: El token
    :param token_type: Tipo de token
    :return: Boolean
    """
    if BlacklistToken.query.filter_by(token=str(token), token_type=str(token_type)).first():
      return True
    else:
      return False