import jwt
from functools import wraps
from flask import request, jsonify
from .models import User
from app import ExpApp, db, bcrypt

def jwt_valid_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        return jsonify({"msg": "_INVALID_TOKEN"}), 400
        return f(*args, **kwargs)
    return wrap


def jwt_valid_token_access(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            token = request.headers["Authorization"].replace("Bearer ", "")
            myJwt = jwt.decode(token, ExpApp().config['JWT_SECRET_KEY'])
            if myJwt["token_type"] == "access":
                myResult = User.check_token(token, 'access')
                if myResult != True:
                    return jsonify({"msg": "_INVALID_TOKEN", "error": myResult}), 400
            else:
                return jsonify({"msg": "_INVALID_TOKEN", "error": '_NO_ACCESS_TOKEN'}), 400
        except:
            return jsonify({"msg": "_INVALID_TOKEN", "error": '_NO_ACCESS_TOKEN'}), 400
        return f(*args, **kwargs)
    return wrap


def jwt_valid_token_refresh(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        try:
            data = request.get_json()
            token = data["refresh"]
            myJwt = jwt.decode(token, ExpApp().config['JWT_SECRET_KEY'])
            if myJwt["token_type"] == "refresh":
                myResult = User.check_token(token, 'refresh')
                if myResult != True:
                    return jsonify({"msg": "_INVALID_TOKEN", "error": myResult}), 400
            else:
                return jsonify({"msg": "_INVALID_TOKEN", "error": '_NO_REFRESH_TOKEN'}), 400
        except:
            return jsonify({"msg": "_INVALID_TOKEN", "error": '_NO_REFRESH_TOKEN'}), 400
        return f(*args, **kwargs)
    return wrap

