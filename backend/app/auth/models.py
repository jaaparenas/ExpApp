import datetime
import uuid

import jwt
from flask import current_app

from ..core.models import BaseModel
from app import db, bcrypt


def _utcnow_naive():
  return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


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
  users = db.relationship('User', secondary=RolesUsers, lazy='subquery', back_populates='roles')

  def __init__(self, name, is_admin=False, is_staff=False, is_guest=False, is_active=True):
    self.name = name
    self.is_admin = is_admin
    self.is_staff = is_staff
    self.is_guest = is_guest
    self.is_active = is_active

class User(db.Model, BaseModel):
  """ Modulo básico de usuario """
  __tablename__ = "users"

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  username = db.Column(db.String(255), unique=True, nullable=False)
  first_name = db.Column(db.String(255), nullable=True)
  last_name = db.Column(db.String(255), nullable=True)
  email = db.Column(db.String(255), unique=True, nullable=False)
  password = db.Column(db.String(255), nullable=False)
  reset_password = db.Column(db.String(255), nullable=True)
  reset_password_expires = db.Column(db.DateTime, nullable=True)
  registered_on = db.Column(db.DateTime, nullable=False)
  is_active = db.Column(db.Boolean, nullable=False, default=False)
  is_admin = db.Column(db.Boolean, nullable=False, default=False)
  token_version = db.Column(db.Integer, nullable=False, default=0)
  roles = db.relationship('Role', secondary=RolesUsers, lazy='subquery', back_populates='users')

  def __init__(self, username, email, password, is_active=False, is_admin=False):
    self.username = username
    self.email = email
    self.password = bcrypt.generate_password_hash(password).decode()
    self.registered_on = _utcnow_naive()
    self.first_name = ""
    self.last_name = ""
    self.is_active = is_active
    self.is_admin = is_admin
    self.token_version = 0

  def encode_tokens(self):
    """
    Genera un par de tokens JWT (access + refresh) con jti, issuer y
    versión de token para poder revocar sesiones.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    secret = current_app.config['JWT_SECRET_KEY']
    issuer = current_app.config.get('JWT_ISSUER', 'expapp')
    access_ttl = int(current_app.config['ACCESS_TOKEN_EXPIRES'])
    refresh_ttl = int(current_app.config['REFRESH_TOKEN_EXPIRES'])

    def build(token_type, ttl):
      return jwt.encode({
        'token_type': token_type,
        'user_id': self.id,
        'ver': self.token_version,
        'jti': uuid.uuid4().hex,
        'iss': issuer,
        'iat': now,
        'exp': now + datetime.timedelta(seconds=ttl),
      }, secret, algorithm='HS256')

    return {
      'access': build('access', access_ttl),
      'refresh': build('refresh', refresh_ttl),
    }

  @staticmethod
  def decode_token(token):
    """Decodifica y valida un token JWT (firma, expiración e issuer)."""
    return jwt.decode(
      token,
      current_app.config['JWT_SECRET_KEY'],
      algorithms=['HS256'],
      issuer=current_app.config.get('JWT_ISSUER', 'expapp'),
      options={'require': ['exp', 'iat', 'jti', 'iss', 'token_type', 'user_id']}
    )

  def invalidate_sessions(self):
    """Invalida todos los tokens emitidos para el usuario."""
    self.token_version = (self.token_version or 0) + 1


class BlacklistToken(db.Model):
  """
  Tokens revocados. Se guarda el ``jti`` (no el token completo) y su
  expiración para poder purgar la tabla periódicamente.
  """
  __tablename__ = 'blacklist_tokens'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
  token_type = db.Column(db.String(10), nullable=False, index=True)
  blacklisted_on = db.Column(db.DateTime, nullable=False)
  expires_at = db.Column(db.DateTime, nullable=False, index=True)

  def __init__(self, jti, token_type='access', expires_at=None):  # nosec B107
    self.jti = jti
    self.token_type = token_type
    self.blacklisted_on = _utcnow_naive()
    self.expires_at = expires_at or _utcnow_naive()

  @staticmethod
  def add(jti, token_type, expires_at):
    if not BlacklistToken.is_blacklisted(jti):
      db.session.add(BlacklistToken(
        jti=jti,
        token_type=token_type,
        expires_at=expires_at
      ))

  @staticmethod
  def is_blacklisted(jti, token_type=None):
    query = BlacklistToken.query.filter_by(jti=str(jti))
    if token_type is not None:
      query = query.filter_by(token_type=str(token_type))
    return query.first() is not None

  @staticmethod
  def purge_expired():
    return BlacklistToken.query.filter(
      BlacklistToken.expires_at < _utcnow_naive()
    ).delete(synchronize_session=False)
