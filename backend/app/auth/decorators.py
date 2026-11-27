from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .models import BlacklistToken, User


def _error(message, error='_INVALID_TOKEN', status=401):
    return jsonify({'msg': message, 'error': error}), status


def _decode_token(token):
    return jwt.decode(
        token,
        current_app.config['JWT_SECRET_KEY'],
        algorithms=['HS256'],
        issuer=current_app.config.get('JWT_ISSUER', 'expapp'),
        options={'require': ['exp', 'iat', 'jti', 'iss', 'token_type', 'user_id']},
    )


def _authenticate(token_type='access', token=None):  # nosec B107
    """Valida un token y devuelve (payload, usuario, respuesta_de_error)."""
    if token is None:
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return None, None, _error('_INVALID_TOKEN', '_NO_AUTHORIZATION_HEADER')
        token = header[len('Bearer '):].strip()

    if not token:
        return None, None, _error('_INVALID_TOKEN', '_NO_TOKEN')

    try:
        payload = _decode_token(token)
    except jwt.PyJWTError:
        return None, None, _error('_INVALID_TOKEN', '_INVALID_TOKEN')

    if payload.get('token_type') != token_type:
        return None, None, _error(
            '_INVALID_TOKEN', '_NO_{}_TOKEN'.format(token_type.upper())
        )

    if BlacklistToken.is_blacklisted(payload.get('jti'), token_type):
        return None, None, _error('_INVALID_TOKEN', '_BANNED_TOKEN')

    user = User.query.filter_by(is_active=True, id=payload.get('user_id')).first()
    if user is None:
        return None, None, _error('_INVALID_USER', '_INVALID_USER')

    if int(payload.get('ver', 0)) != int(user.token_version or 0):
        return None, None, _error('_INVALID_TOKEN', '_REVOKED_TOKEN')

    return payload, user, None


def jwt_valid_token_access(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        payload, user, error = _authenticate('access')
        if error:
            return error
        g.jwt_payload = payload
        g.current_user = user
        return f(*args, **kwargs)
    return wrap


def jwt_valid_token_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        payload, user, error = _authenticate('access')
        if error:
            return error
        if not user.is_admin:
            return _error('_FORBIDDEN', '_NOT_ADMIN', 403)
        g.jwt_payload = payload
        g.current_user = user
        return f(*args, **kwargs)
    return wrap


def jwt_valid_token_refresh(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        data = request.get_json(silent=True) or {}
        token = data.get('refresh')
        if not token or not isinstance(token, str):
            return _error('_INVALID_TOKEN', '_NO_REFRESH_TOKEN')

        payload, user, error = _authenticate('refresh', token)
        if error:
            return error

        g.jwt_payload = payload
        g.current_user = user
        g.refresh_token = token
        return f(*args, **kwargs)
    return wrap
