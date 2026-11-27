from datetime import datetime, timezone

from flask import jsonify, request

from . import core


@core.route("/")
def index():
    user_params = {
        "ip": request.remote_addr,
        'date': datetime.now(timezone.utc)
    }
    return jsonify(user_params), 200


@core.route("/health")
def health():
    return jsonify({"status": "ok"}), 200
