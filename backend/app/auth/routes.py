import datetime
import hashlib
from flask import request, jsonify
from flask_mail import Message
from app import ExpApp, db, bcrypt, mail
from datatables import ColumnDT, DataTables

from . import auth
from .models import User, BlacklistToken, Role
from .decorators import jwt_valid_token_access, jwt_valid_token_refresh


@auth.route('/login', methods=['POST'])
def login():
  # import ipdb; ipdb.set_trace()
  data = request.get_json()

  if not data["username"]:
    return jsonify({"msg": "_NO_USERNAME"}), 400
  if not data["password"]:
    return jsonify({"msg": "_NO_PASSWORD"}), 400

  username = data["username"]
  password = data["password"]
  user = User.query.filter_by(is_active=True, username=username).first()

  if user is not None:
    if bcrypt.check_password_hash(user.password, password):
      jwtTokens = User.encode_tokens(user)
      return jsonify(jwtTokens), 200

  return jsonify({"msg": "_BAD_USERNAME_PASSWORD"}), 400


@auth.route('/register', methods=['POST'])
def register():
  data = request.get_json()

  if not data["username"]:
    return jsonify({"msg": "_NO_USERNAME"}), 400
  if not data["email"]:
    return jsonify({"msg": "_NO_EMAIL"}), 400
  if not data["password"]:
    return jsonify({"msg": "_NO_PASSWORD"}), 400

  username = data["username"]
  email = data["email"]
  password = data["password"]

  user = User(username=username, email=email, password=password)
  db.session.add(user)
  db.session.commit()

  return jsonify({"msg": "_USER_CREATED"}), 201


@auth.route('/data', methods=['GET'])
@jwt_valid_token_access
def user():
  access_token = request.headers["Authorization"].replace("Bearer ", "")
  user_id = User.decode_token(access_token)['user_id']
  if (type(user_id) == int):
    user = User.query.filter_by(is_active=True, id=user_id).first()
    return jsonify({
      "id": user.id,
      "username": user.username,
      "email": user.email,
      "first_name": user.first_name,
      "last_name": user.last_name
    }), 200
  else:
    return jsonify({"msg": "_INVALID_USER"}), 400


@auth.route('/logout', methods=['POST'])
@jwt_valid_token_access
def logout():
  try:
    data = request.get_json()
    jwt_access = request.headers["Authorization"].replace("Bearer ", "")
    jwt_refresh = data["refresh"]

    db_token_access = BlacklistToken(token=jwt_access, token_type='access')
    db_token_refresh = BlacklistToken(token=jwt_refresh, token_type='refresh')
    db.session.add(db_token_access)
    db.session.add(db_token_refresh)
    db.session.commit()

    return jsonify({"msg": "_LOGOUT"}), 200
  except:
    return jsonify({"msg": "_INVALID_USER"}), 400


@auth.route('/refresh', methods=['POST'])
@jwt_valid_token_access
@jwt_valid_token_refresh
def refresh():
  try:
    data = request.get_json()
    jwt_access = request.headers["Authorization"].replace("Bearer ", "")
    jwt_refresh = data["refresh"]

    db_token_access = BlacklistToken(token=jwt_access, token_type='access')
    db_token_refresh = BlacklistToken(token=jwt_refresh, token_type='refresh')
    db.session.add(db_token_access)
    db.session.add(db_token_refresh)
    db.session.commit()

    user_id = User.decode_token(jwt_access)['user_id']
    user = User.query.filter_by(is_active=True, id=user_id).first()
    if user is not None:
      jwtTokens = User.encode_tokens(user)
      return jsonify(jwtTokens), 200
    else:
      return jsonify({"msg": "_INVALID_USER"}), 400
  except:
    return jsonify({"msg": "_INVALID_USER"}), 400


@auth.route('/reset_password_request', methods=['POST'])
def send_reset_password_request():
  try:
    data = request.get_json()
    user = User.query.filter_by(email=data["email"]).first()
    if user is not None:
      reset_token = bcrypt.generate_password_hash(str(datetime.datetime.now()) + str(user.id))
      reset_token = hashlib.md5(reset_token).hexdigest()
      user.reset_password = reset_token
      db.session.commit()

      txtHtmlMesg = "<a href='http://localhost:5000/1.0/user/reset_password/{p_token}'>Password recovery</a>"
      txtHtmlMesg = txtHtmlMesg.format(p_token = reset_token)

      msg = Message("Password recovery", sender="jorge.arenas@expansionti.com", recipients=[user.email])
      msg.html = txtHtmlMesg
      mail.send(msg)

      return jsonify({"msg": "_RESET_PASSWORD"}), 200
    else:
      return jsonify({"msg": "_INVALID_USER"}), 400
  except:
    return jsonify({"msg": "_INVALID_USER"}), 400


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
  try:
    if token != "":
      user = User.query.filter_by(reset_password=token).first()
      if user is not None:
        if request.method == 'POST':
          data = request.get_json()
          if not data["password"] or not data["confirm"] or (data["password"] != data["confirm"]):
            return jsonify({"msg": "_NO_PASSWORD"}), 400
          else:
            password = data["password"]
            user.password = bcrypt.generate_password_hash(password).decode()
            user.reset_password = ""
            db.session.commit()
            return jsonify({"msg": "_UPDATED_PASSWORD"}), 200

    return jsonify({"msg": "_INVALID_TOKEN"}), 400
  except:
    return jsonify({"msg": "_INVALID_TOKEN"}), 400


@auth.route('/users', methods=['GET', 'POST'])
def roles():
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
    rowTable = DataTables(request.get_json()["params"], query, columns)
    return jsonify(rowTable.output_result()), 200