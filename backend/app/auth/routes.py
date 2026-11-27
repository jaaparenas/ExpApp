import datetime
import hashlib
import secrets

import jwt
from flask import current_app, g, jsonify, request
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
from datatables import ColumnDT, DataTables

from app import db, bcrypt, mail, limiter
from . import auth
from .models import User, BlacklistToken
from .decorators import (
  jwt_valid_token_access,
  jwt_valid_token_refresh,
  jwt_valid_token_admin,
)


def _utcnow_naive():
  return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _blacklist_payload(payload):
  """Agrega el jti de un payload ya validado a la lista negra."""
  expires_at = datetime.datetime.fromtimestamp(
    int(payload['exp']), tz=datetime.timezone.utc
  ).replace(tzinfo=None)
  BlacklistToken.add(payload['jti'], payload['token_type'], expires_at)


@auth.route('/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
  data = request.get_json(silent=True) or {}
  username = data.get('username')
  password = data.get('password')

  if not username or not isinstance(username, str):
    return jsonify({"msg": "_NO_USERNAME"}), 400
  if not password or not isinstance(password, str):
    return jsonify({"msg": "_NO_PASSWORD"}), 400

  user = User.query.filter_by(is_active=True, username=username).first()
  if user is not None and bcrypt.check_password_hash(user.password, password):
    current_app.logger.info(
      'login ok user_id=%s ip=%s', user.id, request.remote_addr
    )
    return jsonify(User.encode_tokens(user)), 200

  # Mensaje único: no revela si el usuario existe.
  current_app.logger.warning('login fallido ip=%s', request.remote_addr)
  return jsonify({"msg": "_BAD_USERNAME_PASSWORD"}), 400


@auth.route('/register', methods=['POST'])
@limiter.limit('5 per hour')
def register():
  if not current_app.config.get('ALLOW_REGISTRATION', False):
    return jsonify({"msg": "_REGISTRATION_DISABLED"}), 403

  data = request.get_json(silent=True) or {}
  username = (data.get('username') or '').strip()
  email = (data.get('email') or '').strip().lower()
  password = data.get('password') or ''

  if not username:
    return jsonify({"msg": "_NO_USERNAME"}), 400
  if not email:
    return jsonify({"msg": "_NO_EMAIL"}), 400
  if not password:
    return jsonify({"msg": "_NO_PASSWORD"}), 400
  if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
    return jsonify({"msg": "_WEAK_PASSWORD"}), 400

  if User.query.filter((User.username == username) | (User.email == email)).first():
    return jsonify({"msg": "_USER_EXISTS"}), 409

  user = User(username=username, email=email, password=password, is_active=True)
  db.session.add(user)
  try:
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({"msg": "_USER_EXISTS"}), 409

  current_app.logger.info('registro user_id=%s ip=%s', user.id, request.remote_addr)
  return jsonify({"msg": "_USER_CREATED"}), 201


@auth.route('/data', methods=['GET'])
@jwt_valid_token_access
def user():
  user = g.current_user
  return jsonify({
    "id": user.id,
    "username": user.username,
    "email": user.email,
    "first_name": user.first_name,
    "last_name": user.last_name,
    "is_admin": user.is_admin
  }), 200


@auth.route('/logout', methods=['POST'])
@limiter.limit('30 per minute')
def logout():
  """Cierra la sesión. No exige un access válido: si ya expiró, igualmente
  revoca el refresh token para que no pueda reutilizarse."""
  data = request.get_json(silent=True) or {}
  refresh_token = data.get('refresh')
  access_token = request.headers.get('Authorization', '')[len('Bearer '):].strip()

  user_id = None
  if access_token:
    try:
      access_payload = User.decode_token(access_token)
      if access_payload.get('token_type') == 'access':
        _blacklist_payload(access_payload)
        user_id = access_payload.get('user_id')
    except jwt.PyJWTError:
      pass

  if isinstance(refresh_token, str) and refresh_token:
    try:
      refresh_payload = User.decode_token(refresh_token)
      if refresh_payload.get('token_type') == 'refresh':
        _blacklist_payload(refresh_payload)
        user_id = user_id or refresh_payload.get('user_id')
    except jwt.PyJWTError:
      pass

  try:
    db.session.commit()
  except Exception:
    db.session.rollback()
    current_app.logger.exception('No se pudo cerrar la sesión')
    return jsonify({"msg": "_LOGOUT_ERROR"}), 400

  current_app.logger.info('logout user_id=%s', user_id)
  return jsonify({"msg": "_LOGOUT"}), 200


@auth.route('/refresh', methods=['POST'])
@limiter.limit('30 per minute')
@jwt_valid_token_refresh
def refresh():
  user = g.current_user
  _blacklist_payload(g.jwt_payload)

  try:
    BlacklistToken.purge_expired()
    db.session.commit()
  except Exception:
    db.session.rollback()
    current_app.logger.exception('No se pudo rotar el refresh token')
    return jsonify({"msg": "_INVALID_TOKEN"}), 401

  return jsonify(User.encode_tokens(user)), 200


@auth.route('/change_password', methods=['POST'])
@limiter.limit('5 per minute')
@jwt_valid_token_access
def change_password():
  data = request.get_json(silent=True) or {}
  current_password = data.get('current_password') or ''
  password = data.get('password') or ''
  confirm = data.get('confirm') or ''

  if not bcrypt.check_password_hash(g.current_user.password, current_password):
    return jsonify({"msg": "_BAD_PASSWORD"}), 400
  if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
    return jsonify({"msg": "_WEAK_PASSWORD"}), 400
  if password != confirm:
    return jsonify({"msg": "_PASSWORD_MISMATCH"}), 400

  g.current_user.password = bcrypt.generate_password_hash(password).decode()
  g.current_user.invalidate_sessions()
  db.session.commit()

  current_app.logger.info('password cambiado user_id=%s', g.current_user.id)
  return jsonify({"msg": "_UPDATED_PASSWORD"}), 200


@auth.route('/reset_password_request', methods=['POST'])
@limiter.limit('5 per minute')
def send_reset_password_request():
  data = request.get_json(silent=True) or {}
  email = (data.get('email') or '').strip().lower()
  if not email:
    return jsonify({"msg": "_NO_EMAIL"}), 400

  user = User.query.filter_by(email=email).first()
  if user is not None:
    # Se guarda solo el hash; el token en claro viaja únicamente por correo.
    raw_token = secrets.token_urlsafe(32)
    user.reset_password = hashlib.sha256(raw_token.encode()).hexdigest()
    user.reset_password_expires = _utcnow_naive() + datetime.timedelta(
      seconds=int(current_app.config['RESET_TOKEN_EXPIRES'])
    )
    db.session.commit()

    reset_url = '{frontend}/reset-password?token={token}'.format(
      frontend=current_app.config['FRONTEND_URL'].rstrip('/'),
      token=raw_token
    )
    msg = Message(
      "Password recovery",
      sender=current_app.config['MAIL_DEFAULT_SENDER'],
      recipients=[user.email]
    )
    msg.html = "<a href='{url}'>Password recovery</a>".format(url=reset_url)
    try:
      mail.send(msg)
    except Exception:
      current_app.logger.exception('No se pudo enviar el correo de recuperación')

  # Respuesta genérica: no permite enumerar correos registrados.
  return jsonify({"msg": "_RESET_PASSWORD"}), 200


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
def reset_password(token):
  if not token:
    return jsonify({"msg": "_INVALID_TOKEN"}), 400

  token_hash = hashlib.sha256(token.encode()).hexdigest()
  user = User.query.filter_by(reset_password=token_hash).first()
  if user is None:
    return jsonify({"msg": "_INVALID_TOKEN"}), 400

  if (user.reset_password_expires is None or
      user.reset_password_expires < _utcnow_naive()):
    user.reset_password = ""  # nosec B105
    user.reset_password_expires = None
    db.session.commit()
    return jsonify({"msg": "_EXPIRED_TOKEN"}), 400

  if request.method == 'POST':
    data = request.get_json(silent=True) or {}
    password = data.get('password') or ''
    confirm = data.get('confirm') or ''
    if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
      return jsonify({"msg": "_WEAK_PASSWORD"}), 400
    if password != confirm:
      return jsonify({"msg": "_PASSWORD_MISMATCH"}), 400

    user.password = bcrypt.generate_password_hash(password).decode()
    user.reset_password = ""  # nosec B105
    user.reset_password_expires = None
    user.invalidate_sessions()
    db.session.commit()

    current_app.logger.info('password restablecido user_id=%s', user.id)
    return jsonify({"msg": "_UPDATED_PASSWORD"}), 200

  return jsonify({"msg": "_VALID_TOKEN"}), 200


@auth.route('/users', methods=['GET', 'POST'])
@limiter.limit('60 per minute')
@jwt_valid_token_admin
def users():
  payload = request.get_json(silent=True) or {}
  params = payload.get('params')
  if not isinstance(params, dict):
    return jsonify({"msg": "_INVALID_PARAMS"}), 400

  columns = [
    ColumnDT(User.id),
    ColumnDT(User.username),
    ColumnDT(User.first_name),
    ColumnDT(User.last_name),
    ColumnDT(User.email),
    ColumnDT(User.is_active),
    ColumnDT(User.is_admin)
  ]
  query = db.session.query().select_from(User)
  rowTable = DataTables(params, query, columns)
  return jsonify(rowTable.output_result()), 200
