from . import core
from flask import jsonify, request, redirect
from datetime import datetime, timedelta


@core.route("/")
def index():
    user_params = {
        "ip" : request.remote_addr,
        'date' : datetime.utcnow()
    }
    return jsonify(user_params), 201