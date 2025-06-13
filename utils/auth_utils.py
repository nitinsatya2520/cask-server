#auth_utils.py
from functools import wraps
from flask import request, jsonify
import jwt
import logging
import os
import datetime
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")  # Use this at top

# Enable basic logging
logging.basicConfig(level=logging.INFO)

def decode_token_from_header():
    if 'Authorization' in request.headers:
        bearer = request.headers['Authorization']
        if bearer.startswith("Bearer "):
            return bearer.split(" ")[1]
    return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = decode_token_from_header()
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = data["user_id"]
            request.role = data.get("role", "user")
            logging.info(f"[TOKEN] User ID: {request.user_id}, Role: {request.role}")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = decode_token_from_header()
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if data.get("role") != "admin":
                return jsonify({"message": "Admin access required"}), 403
            request.user_id = data["user_id"]
            request.role = "admin"
            logging.info(f"[ADMIN] Access granted for Admin ID: {request.user_id}")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 401

        return f(*args, **kwargs)
    return decorated


def create_jwt_token(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
